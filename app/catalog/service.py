"""Catalog retrieval, ranking, details, and availability service."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from app.catalog.repository import CatalogRepository
from app.catalog.schemas import (
    BranchView,
    ProductDetails,
    ProductSearchRequest,
    ProductSearchResponse,
    ProductView,
    VariantView,
    BranchAvailabilityView,
    StoreContext,
)
from app.config import get_config
from app.common.exceptions import NotFoundError

LOCAL_IMAGE_ROUTE = "/assets/products/"


class CatalogService:
    """Public entry point for product and inventory retrieval.

    API routes and the future clothing agent should use this service contract.
    SQLAlchemy queries remain private inside :class:`CatalogRepository`.
    """

    def __init__(
        self,
        repository: CatalogRepository,
        *,
        product_images_dir: Path | None = None,
        promotions: Any = None,
    ) -> None:
        self._repository = repository
        self._promotions = promotions
        self._product_images_dir = product_images_dir or get_config().product_images_dir
        self._image_url_cache: dict[str, str | None] = {}

    async def search(self, request: ProductSearchRequest) -> ProductSearchResponse:
        """Search and rank products using deterministic filters."""
        working = request.model_copy(update={"limit": min(request.limit, 20)})
        rows = await self._repository.search_rows(working)
        relaxed: list[str] = []

        if request.allow_relaxation and not rows and request.size_mapping:
            working = working.model_copy(update={"size_mapping": {}})
            relaxed.append("size")
            rows = await self._repository.search_rows(working)
        if request.allow_relaxation and not rows and request.colors:
            working = working.model_copy(update={"colors": []})
            relaxed.append("color")
            rows = await self._repository.search_rows(working)
        if request.allow_relaxation and not rows and request.branch_code:
            working = working.model_copy(update={"branch_code": None})
            relaxed.append("branch")
            rows = await self._repository.search_rows(working)
        if request.allow_relaxation and not rows and request.in_stock_only:
            working = working.model_copy(update={"in_stock_only": False})
            relaxed.append("stock")
            rows = await self._repository.search_rows(working)
        if request.allow_relaxation and not rows and request.maximum_price is not None:
            expanded_budget = (request.maximum_price * Decimal("1.15")).quantize(
                Decimal("0.01")
            )
            working = working.model_copy(update={"maximum_price": expanded_budget})
            relaxed.append("budget_15_percent")
            rows = await self._repository.search_rows(working)
            
        if request.allow_relaxation and not rows and request.maximum_price is not None:
            working = working.model_copy(update={"maximum_price": None})
            relaxed.append("budget_dropped")
            rows = await self._repository.search_rows(working)

        offers = []
        if self._promotions:
            offers = await self._promotions._repository.get_active_offers()

        products = self._group_rows_into_products(rows, offers)
        
        # Implement deterministic multi-category balancing if multiple categories were requested
        if len(request.categories) > 1 and products:
            balanced = []
            category_groups = {}
            for p in products:
                # Use a case-insensitive check to group properly
                matched_cat = p.category
                for req_cat in request.categories:
                    if req_cat.lower() in p.category.lower():
                        matched_cat = req_cat
                        break
                category_groups.setdefault(matched_cat, []).append(p)
                
            # target per category is limit // num_categories
            target_per_cat = max(1, request.limit // len(request.categories))
            
            # 1st pass: take up to target from each category
            remaining = []
            for cat, prods in category_groups.items():
                balanced.extend(prods[:target_per_cat])
                remaining.extend(prods[target_per_cat:])
                
            # 2nd pass: fill the rest up to limit from remaining products
            if len(balanced) < request.limit and remaining:
                needed = request.limit - len(balanced)
                balanced.extend(remaining[:needed])
                
            # Preserve some logical order: group by category, then by original rank
            products = sorted(balanced, key=lambda x: (x.category, -len([v for v in x.variants if v.is_available])))

        # Apply ranking based on original DB ordering which is preserved in products map insertion order.
        return ProductSearchResponse(
            products=products[:request.limit],
            result_count=len(products[:request.limit]),
            relaxed_constraints=relaxed,
        )

    def _group_rows_into_products(self, rows: list[dict[str, Any]], offers: list[Any] | None = None) -> list[ProductView]:
        """Group flattened database rows into the structured ProductView contract."""
        offers = offers or []
        products_map = {}
        for r in rows:
            row = self._with_resolved_image(r)
            pid = row["product_id"]
            if pid not in products_map:
                products_map[pid] = {
                    "product_id": pid,
                    "article_code": row["article_code"],
                    "product_name": row["product_name"],
                    "description": row.get("description"),
                    "category": row["category"],
                    "subcategory": None,
                    "product_type": row.get("product_type", "unknown"),
                    "gender": row["gender"],
                    "brand": row["brand"],
                    "material": row.get("material"),
                    "fit": row.get("fit"),
                    "season": row.get("season"),
                    "occasion": row.get("occasion"),
                    "base_price": row["price"], # Default, recalculated later
                    "final_price": row["price"],
                    "discount_amount": Decimal("0.00"),
                    "applied_offer": None,
                    "images": [row["image_url"]] if row.get("image_url") else [],
                    "variants_map": {}
                }
            
            p_map = products_map[pid]
            if row.get("image_url") and row["image_url"] not in p_map["images"]:
                p_map["images"].append(row["image_url"])
                
            vid = row["variant_id"]
            if vid not in p_map["variants_map"]:
                # Evaluate promotions for this variant
                base_price = Decimal(str(row["price"]))
                final_price = base_price
                best_discount = Decimal("0.00")
                applied_offer = None
                
                for offer in offers:
                    is_eligible = False
                    if offer.target_scope in ("GLOBAL", "STORE_WIDE"):
                        is_eligible = True
                    elif offer.target_scope == "BRANCH" and offer.target_branch_id == row["branch_id"]:
                        is_eligible = True
                    elif offer.target_scope == "PRODUCT" and offer.target_product_id == pid:
                        is_eligible = True
                    elif offer.target_scope == "VARIANT" and offer.target_variant_id == vid:
                        is_eligible = True
                        
                    if is_eligible:
                        # For catalog view, we assume quantity = 1 and no min_cart_value constraint can be met unless 0
                        # If an offer requires min_cart_value > base_price, it might not apply, but we'll show it if min_cart_value is 0 or low enough.
                        if offer.min_cart_value and base_price < offer.min_cart_value:
                            continue
                        if offer.min_quantity and offer.min_quantity > 1:
                            continue
                            
                        discount = Decimal("0.00")
                        if offer.benefit_type == "PERCENTAGE" and offer.discount_percentage:
                            discount = base_price * (offer.discount_percentage / Decimal("100"))
                        elif offer.benefit_type == "FIXED" and offer.discount_amount:
                            discount = offer.discount_amount
                            
                        if discount > best_discount:
                            best_discount = discount
                            from app.promotions.schemas import OfferSummary
                            applied_offer = OfferSummary(
                                offer_code=offer.offer_code,
                                offer_name=offer.offer_name,
                                description=offer.description,
                                discount_amount=offer.discount_amount,
                                discount_percentage=offer.discount_percentage,
                                benefit_type=offer.benefit_type
                            )
                
                final_price = max(base_price - best_discount, Decimal("0.00"))
                
                p_map["variants_map"][vid] = {
                    "variant_id": vid,
                    "sku": row["sku"],
                    "color": row["color"],
                    "size": row["size"],
                    "price": base_price,
                    "final_price": final_price,
                    "discount_amount": best_discount,
                    "applied_offer": applied_offer,
                    "is_available": False,
                    "branch_availability": []
                }
            
            v_map = p_map["variants_map"][vid]
            available_qty = max(int(row.get("available_quantity") or 0), 0)
            
            v_map["branch_availability"].append(BranchAvailabilityView(
                branch_id=row["branch_id"],
                branch_code=row["branch_code"],
                branch_name=row["branch_name"],
                is_available=available_qty > 0,
                available_quantity=available_qty
            ))
            
            if available_qty > 0:
                v_map["is_available"] = True
                
        # Finalize list
        results = []
        for p in products_map.values():
            variants = [VariantView(**v) for v in p["variants_map"].values()]
            p["variants"] = variants
            
            # Aggregate product-level pricing (take the minimum final_price among variants to show "From X")
            if variants:
                min_variant = min(variants, key=lambda v: v.final_price)
                p["base_price"] = min_variant.price
                p["final_price"] = min_variant.final_price
                p["discount_amount"] = min_variant.discount_amount
                p["applied_offer"] = min_variant.applied_offer
            else:
                p["base_price"] = Decimal("0.00")
                p["final_price"] = Decimal("0.00")
                
            del p["variants_map"]
            results.append(ProductView(**p))
            
        return results

    async def get_menu(self) -> list[dict[str, Any]]:
        """Return a menu of products grouped by actual database categories."""
        wide = await self.search(
            ProductSearchRequest(
                in_stock_only=True,
                allow_relaxation=False,
                limit=150,
            )
        )
        groups: dict[str, list] = {}
        for product in wide.products:
            cat = product.category or "General"
            if cat not in groups:
                groups[cat] = []
            if len(groups[cat]) < 10:
                groups[cat].append(product)

        preferred_order = [
            "T-Shirts", "Polo Shirts", "Cotton Shirts", "Formal Shirts",
            "Jeans", "Trousers", "Cotton Pants", "Cargo Pants",
            "Shorts", "Hoodies", "Gym Wear", "Track Pants",
        ]
        menu = []
        seen = set()
        for cat_name in preferred_order:
            if cat_name in groups and groups[cat_name]:
                menu.append({"category_name": str(cat_name), "products": groups[cat_name]})
                seen.add(cat_name)
        for cat_name, products in groups.items():
            if cat_name not in seen and products:
                menu.append({"category_name": str(cat_name), "products": products})
        return menu

    async def get_product(self, product_id: int) -> ProductDetails:
        """Return product metadata and all active branch-specific options."""
        metadata = await self._repository.product_metadata(product_id)
        if not metadata:
            raise NotFoundError("Product was not found.", code="PRODUCT_NOT_FOUND")

        rows = await self._repository.search_rows(
            ProductSearchRequest(in_stock_only=False, allow_relaxation=False, limit=1),
            product_id=product_id,
            database_limit=300,
        )
        offers = []
        if self._promotions:
            offers = await self._promotions._repository.get_active_offers()

        products = self._group_rows_into_products(rows, offers)
        if not products:
            raise NotFoundError("Product was not found.", code="PRODUCT_NOT_FOUND")
            
        product = products[0]
        # Fetch all exact image paths
        all_images = await self._repository.image_urls(product_id)
        product.images = [
            url for url in (self._resolve_image_url(i) for i in all_images) if url
        ]
        
        return ProductDetails(product=product)

    async def list_branches(self) -> list[BranchView]:
        """Return the active branches available for filtering and stock display."""
        return [BranchView(**row) for row in await self._repository.list_branches()]

    async def get_store_context(self) -> StoreContext:
        """Return the dynamic store context for the agent."""
        branches = await self.list_branches()
        distinct_vals = await self._repository.get_distinct_values()
        
        return StoreContext(
            store_name="Northstar Menswear",
            store_id="northstar",
            branches=branches,
            categories=distinct_vals["categories"],
            subcategories=[],
            product_types=distinct_vals["product_types"],
            supported_attributes=["color", "size", "fit", "material", "season", "occasion"],
            sizes=distinct_vals["sizes"],
            colors=distinct_vals["colors"],
            seasons=distinct_vals["seasons"],
            occasions=distinct_vals["occasions"],
            capabilities=[
                "Catalog Browsing",
                "Dynamic Filtering",
                "Branch Stock Checking",
                "Promotions Evaluation",
                "Cart Management",
                "Checkout Preview",
                "Order Placement"
            ]
        )

    def _with_resolved_image(self, row: dict[str, Any]) -> dict[str, Any]:
        """Return a copy with a browser-safe product image URL."""
        item = dict(row)
        item["image_url"] = self._resolve_image_url(item.get("image_url"))
        return item

    def _resolve_image_url(self, image_url: str | None) -> str | None:
        """Normalize local product image paths and suppress missing assets."""
        if not image_url:
            return None

        raw_url = image_url.strip()
        if not raw_url:
            return None
        if raw_url in self._image_url_cache:
            return self._image_url_cache[raw_url]

        parsed = urlsplit(raw_url)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            self._image_url_cache[raw_url] = raw_url
            return raw_url
        if parsed.scheme or parsed.netloc:
            self._image_url_cache[raw_url] = None
            return None

        path = parsed.path.replace("\\", "/").lstrip("/")
        if path.startswith("assets/products/"):
            relative = path.removeprefix("assets/products/")
        elif path.startswith("assets/"):
            relative = path.removeprefix("assets/")
        elif path.startswith("products/"):
            relative = path.removeprefix("products/")
        else:
            relative = path

        parts = PurePosixPath(relative).parts
        if not parts or any(part in {"", ".", ".."} for part in parts):
            self._image_url_cache[raw_url] = None
            return None

        root = self._product_images_dir.resolve()
        file_path = root.joinpath(*parts).resolve()
        if not file_path.is_relative_to(root) or not file_path.is_file():
            self._image_url_cache[raw_url] = None
            return None

        resolved = f"{LOCAL_IMAGE_ROUTE}{'/'.join(parts)}"
        self._image_url_cache[raw_url] = resolved
        return resolved
