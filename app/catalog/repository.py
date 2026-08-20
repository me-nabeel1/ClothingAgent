"""SQLAlchemy retrieval queries for catalog and inventory data."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.catalog.models import (
    Branch,
    Category,
    Color,
    Product,
    ProductImage,
    ProductVariant,
    Size,
)
from app.inventory.models import BranchInventory
from app.catalog.schemas import ProductSearchRequest


class CatalogRepository:
    """Read catalog data without exposing SQLAlchemy objects to API layers."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def search_rows(
        self,
        request: ProductSearchRequest,
        *,
        product_id: int | None = None,
        database_limit: int = 120,
    ) -> list[dict[str, Any]]:
        """Return flattened variant/branch rows matching structured filters."""

        conditions = [
            Product.product_status == "ACTIVE",
            ProductVariant.is_active.is_(True),
            Branch.is_active.is_(True),
            Product.gender == "MEN",
        ]
        if product_id is not None:
            conditions.append(Product.product_id == product_id)
        if request.categories:
            matching_categories = []
            parent = aliased(Category)
            for category in request.categories:
                raw_term = category.strip().lower()
                clean_term = raw_term.replace("-", "").replace(" ", "")

                if clean_term in ("tshirt", "tshirts", "tee", "tees"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "t-shirts",
                        func.lower(Category.category_code) == "tshirts",
                        func.lower(Category.category_name).contains("t-shirt"),
                        func.lower(Category.category_code).contains("tshirt"),
                    ]
                elif clean_term in ("shirt", "shirts"):
                    conditions_for_category = [
                        and_(
                            or_(
                                func.lower(Category.category_name) == "shirts",
                                func.lower(Category.category_code) == "shirts",
                                func.lower(Category.category_name).contains("shirt"),
                            ),
                            ~func.lower(Category.category_name).contains("t-shirt"),
                            ~func.lower(Category.category_code).contains("tshirt"),
                        )
                    ]
                elif clean_term in ("pant", "pants"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "pants",
                        func.lower(Category.category_code) == "pants",
                        func.lower(Category.category_name).contains("pant"),
                    ]
                elif clean_term in ("trouser", "trousers"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "trousers",
                        func.lower(Category.category_name).contains("trouser"),
                    ]
                elif clean_term in ("jean", "jeans", "denim"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "jeans",
                        func.lower(Category.category_code) == "jeans",
                        func.lower(Category.category_name).contains("jean"),
                    ]
                elif clean_term in ("traditional", "kurta", "shalwar"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "traditional",
                        func.lower(Category.category_code) == "traditional",
                        func.lower(Category.category_name).contains("traditional"),
                    ]
                elif clean_term in ("outerwear", "hoodie", "jacket"):
                    conditions_for_category = [
                        func.lower(Category.category_name) == "outerwear",
                        func.lower(Category.category_code) == "outerwear",
                        func.lower(Category.category_name).contains("outerwear"),
                    ]
                else:
                    conditions_for_category = [
                        func.lower(Category.category_name).contains(raw_term),
                        func.replace(func.replace(func.lower(Category.category_name), "-", ""), " ", "").contains(clean_term),
                        func.lower(Category.category_code).contains(clean_term),
                        func.lower(parent.category_name).contains(raw_term),
                    ]

                query = (
                    select(Category.category_id)
                    .outerjoin(parent, Category.parent_category_id == parent.category_id)
                    .where(or_(*conditions_for_category))
                )
                matching_categories.append(query)

            conditions.append(or_(*[Product.category_id.in_(q) for q in matching_categories]))
        if request.colors:
            conditions.append(
                func.lower(Color.color_name).in_([value.lower() for value in request.colors])
            )
        if request.excluded_colors:
            conditions.append(
                func.lower(Color.color_name).not_in(
                    [value.lower() for value in request.excluded_colors]
                )
            )
        if request.excluded_product_ids:
            conditions.append(Product.product_id.not_in(request.excluded_product_ids))
        if request.size_mapping:
            size_conditions = []
            for target, sz in request.size_mapping.items():
                target_term = target.strip().lower()
                # Check if it matches a category name, product type, or just globally apply if 'all' or unknown.
                size_conditions.append(
                    and_(
                        Size.size_label == sz,
                        or_(
                            func.lower(Category.category_name).contains(target_term),
                            func.lower(Product.product_type).contains(target_term),
                            func.lower(Product.product_name).contains(target_term)
                        )
                    )
                )
            if size_conditions:
                conditions.append(or_(*size_conditions))
        if request.minimum_price is not None:
            conditions.append(ProductVariant.selling_price >= request.minimum_price)
        if request.maximum_price is not None:
            conditions.append(ProductVariant.selling_price <= request.maximum_price)
        if request.branch_code:
            conditions.append(func.lower(Branch.branch_code) == request.branch_code.lower())
        if request.materials:
            conditions.append(
                or_(*[Product.material.ilike(f"%{value}%") for value in request.materials])
            )
        if request.fits:
            conditions.append(
                func.lower(Product.fit).in_([value.lower() for value in request.fits])
            )
        if request.seasons:
            conditions.append(
                func.lower(Product.season).in_([value.lower() for value in request.seasons])
            )
        if request.product_types:
            conditions.append(
                func.lower(Product.product_type).in_([value.lower() for value in request.product_types])
            )
        if request.occasions:
            conditions.append(
                func.lower(Product.occasion).in_([value.lower() for value in request.occasions])
            )
        if request.article_code:
            conditions.append(func.lower(Product.article_code) == request.article_code.lower())
        if request.sku:
            conditions.append(func.lower(ProductVariant.sku) == request.sku.lower())
        if request.semantic_tags:
            # The existing demo database does not contain a dedicated tags
            # column. Match semantic needs against the descriptive fields that
            # are actually present in the deployed-app schema.
            semantic_columns = (
                Product.product_name,
                Product.description,
                Product.material,
                Product.fit,
                Product.season,
                Category.category_name,
            )
            conditions.append(
                or_(
                    *[
                        column.ilike(f"%{tag}%")
                        for tag in request.semantic_tags
                        for column in semantic_columns
                    ]
                )
            )

        structured_filters_present = any(
            (
                request.categories,
                request.colors,
                request.excluded_colors,
                request.size_mapping,
                request.minimum_price is not None,
                request.maximum_price is not None,
                request.branch_code,
                request.materials,
                request.fits,
                request.seasons,
                request.product_types,
                request.occasions,
                request.article_code,
                request.sku,
            )
        )
        if request.query_text and not request.semantic_tags:
            raw_text = request.query_text.lower()
            tokens = [
                t for t in re.findall(r"[a-zA-Z0-9-]+", raw_text)
                if len(t) >= 2 and t not in {"show", "find", "need", "want", "with", "please", "tell", "more", "about", "the", "for", "look", "looking"}
            ][:8]

            if tokens:
                token_conditions = []
                for token in tokens:
                    clean_tok = token.replace("-", "")
                    if clean_tok in ("tshirt", "tshirts", "tee", "tees"):
                        token_conditions.append(
                            or_(
                                func.lower(Category.category_name).contains("t-shirt"),
                                func.lower(Category.category_code).contains("tshirt"),
                                Product.product_name.ilike("%t-shirt%"),
                                Product.product_name.ilike("%tee%"),
                            )
                        )
                    else:
                        from app.common.helpers import normalize_size_label, normalize_color_name
                        norm_sz = normalize_size_label(token)
                        norm_col = normalize_color_name(token)
                        
                        searchable_columns = [
                            Product.product_name.ilike(f"%{token}%"),
                            Product.description.ilike(f"%{token}%"),
                            Product.material.ilike(f"%{token}%"),
                            Product.fit.ilike(f"%{token}%"),
                            Product.season.ilike(f"%{token}%"),
                            Category.category_name.ilike(f"%{token}%"),
                            Color.color_name.ilike(f"%{token}%"),
                            Color.color_name.ilike(f"%{norm_col}%"),
                            Size.size_label.ilike(f"%{token}%"),
                            Size.size_label.ilike(f"%{norm_sz}%"),
                        ]
                        token_conditions.append(or_(*searchable_columns))
                conditions.append(and_(*token_conditions))

        available = self._available_quantity_expression()
        
        # Enforce max upper bound of 100
        limit = min(request.limit, 100) if request.limit else 100
        
        # Step 1: Find matching product IDs first to respect limit properly.
        product_query = (
            select(Product.product_id, Category.category_id)
            .select_from(ProductVariant)
            .join(Product, Product.product_id == ProductVariant.product_id)
            .join(Category, Category.category_id == Product.category_id)
            .join(Color, Color.color_id == ProductVariant.color_id)
            .join(Size, Size.size_id == ProductVariant.size_id)
            .join(BranchInventory, BranchInventory.variant_id == ProductVariant.variant_id)
            .join(Branch, Branch.branch_id == BranchInventory.branch_id)
            .where(and_(*conditions))
        )
        
        # Determine sorting for ranking
        # Bypass in_stock_only filter if this is an exact article lookup
        if request.in_stock_only and not request.article_code and not request.sku and product_id is None:
            product_query = product_query.where(available > 0)
            
        product_query = (
            product_query
            .group_by(Product.product_id, Category.category_id)
            .order_by(
                func.max(available).desc(), 
                func.min(ProductVariant.selling_price).asc()
            )
        )
        
        rows = (await self._db.execute(product_query)).all()
        if not rows:
            return []
            
        # Group product IDs by category to enforce deterministic distribution
        from collections import defaultdict
        category_to_products = defaultdict(list)
        for row in rows:
            category_to_products[row.category_id].append(row.product_id)
            
        selected_ids = []
        remaining_limit = limit
        
        # Round-robin selection to balance across categories
        while remaining_limit > 0 and category_to_products:
            per_cat = max(1, remaining_limit // len(category_to_products))
            cats_to_remove = []
            
            for cat_id, p_ids in list(category_to_products.items()):
                take_count = min(len(p_ids), per_cat)
                if take_count > 0:
                    selected_ids.extend(p_ids[:take_count])
                    category_to_products[cat_id] = p_ids[take_count:]
                    remaining_limit -= take_count
                    
                if not category_to_products[cat_id]:
                    cats_to_remove.append(cat_id)
                    
                if remaining_limit <= 0:
                    break
                    
            for cat in cats_to_remove:
                if cat in category_to_products:
                    del category_to_products[cat]
                    
        product_ids = selected_ids

        # Step 2: Fetch full flattened details for these specific products
        result = await self._db.execute(
            self._base_statement()
            .where(Product.product_id.in_(product_ids))
        )
        return [dict(row) for row in result.mappings().all()]

    async def product_metadata(self, product_id: int) -> dict[str, Any] | None:
        """Return product-level metadata independent of variants and branches."""

        result = await self._db.execute(
            select(
                Product.product_id,
                Product.article_code,
                Product.product_name,
                Category.category_name.label("category"),
                Product.gender,
                Product.brand,
                Product.material,
                Product.fit,
                Product.season,
                Product.description,
            )
            .join(Category, Category.category_id == Product.category_id)
            .where(
                Product.product_id == product_id, 
                Product.product_status == "ACTIVE",
                Product.gender == "MEN"
            )
            .limit(1)
        )
        row = result.mappings().first()
        return dict(row) if row else None


    async def image_urls(self, product_id: int) -> list[str]:
        """Return product image paths in display order."""

        result = await self._db.scalars(
            select(ProductImage.image_path)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.display_order, ProductImage.image_id)
        )
        return list(result.all())

    async def list_branches(self) -> list[dict[str, Any]]:
        """Return active branches in stable display order."""

        result = await self._db.execute(
            select(
                Branch.branch_id,
                Branch.branch_code,
                Branch.branch_name,
                Branch.city,
                Branch.address,
            )
            .where(Branch.is_active.is_(True))
            .order_by(Branch.city, Branch.branch_name)
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_distinct_values(self) -> dict[str, list[str]]:
        """Return all available catalog vocabulary dynamically."""
        
        categories = (await self._db.scalars(select(Category.category_name).distinct())).all()
        product_types = (await self._db.scalars(select(Product.product_type).distinct())).all()
        occasions = (await self._db.scalars(select(Product.occasion).where(Product.occasion != None).distinct())).all()
        sizes = (await self._db.scalars(select(Size.size_label).distinct())).all()
        colors = (await self._db.scalars(select(Color.color_name).distinct())).all()
        seasons = (await self._db.scalars(select(Product.season).where(Product.season != None).distinct())).all()
        
        return {
            "categories": sorted(list(categories)),
            "product_types": sorted([p for p in product_types if p and p != "unknown"]),
            "occasions": sorted(list(occasions)),
            "sizes": list(sizes), # maybe sort later
            "colors": sorted(list(colors)),
            "seasons": sorted(list(seasons)),
        }

    async def availability_row(
        self,
        variant_id: int,
        branch_id: int,
    ) -> dict[str, Any] | None:
        """Return availability for one exact variant and branch."""

        result = await self._db.execute(
            self._base_statement()
            .where(
                ProductVariant.variant_id == variant_id,
                Branch.branch_id == branch_id,
                Product.product_status == "ACTIVE",
                Product.gender == "MEN",
                ProductVariant.is_active.is_(True),
                Branch.is_active.is_(True),
            )
            .limit(1)
        )
        row = result.mappings().first()
        return dict(row) if row else None

    @staticmethod
    def _available_quantity_expression():
        """Return the reusable SQLAlchemy expression for sellable stock."""

        return (
            BranchInventory.quantity_on_hand
            - BranchInventory.reserved_quantity
            - BranchInventory.damaged_quantity
        )

    @classmethod
    def _base_statement(cls) -> Select:
        """Build the common flattened product/variant/branch query."""

        available = cls._available_quantity_expression().label("available_quantity")
        primary_image = (
            select(ProductImage.image_path)
            .where(
                ProductImage.product_id == Product.product_id
            )
            .order_by(
                (ProductImage.color_id == ProductVariant.color_id).desc(),
                ProductImage.is_primary.desc(),
                ProductImage.display_order
            )
            .limit(1)
            .scalar_subquery()
        )
        return (
            select(
                Product.product_id.label("product_id"),
                ProductVariant.variant_id.label("variant_id"),
                Branch.branch_id.label("branch_id"),
                Product.article_code.label("article_code"),
                ProductVariant.sku.label("sku"),
                Product.product_name.label("product_name"),
                Category.category_name.label("category"),
                Product.product_type.label("product_type"),
                Product.occasion.label("occasion"),
                Product.gender.label("gender"),
                Product.brand.label("brand"),
                Color.color_name.label("color"),
                Size.size_label.label("size"),
                ProductVariant.selling_price.label("price"),
                Branch.branch_code.label("branch_code"),
                Branch.branch_name.label("branch_name"),
                Branch.city.label("city"),
                available,
                BranchInventory.in_transit_quantity.label("in_transit_quantity"),
                primary_image.label("image_url"),
                Product.material.label("material"),
                Product.fit.label("fit"),
                Product.season.label("season"),
                Product.description.label("description"),
            )
            .select_from(ProductVariant)
            .join(Product, Product.product_id == ProductVariant.product_id)
            .join(Category, Category.category_id == Product.category_id)
            .join(Color, Color.color_id == ProductVariant.color_id)
            .join(Size, Size.size_id == ProductVariant.size_id)
            .join(BranchInventory, BranchInventory.variant_id == ProductVariant.variant_id)
            .join(Branch, Branch.branch_id == BranchInventory.branch_id)
        )
