"""Catalog retrieval, ranking, details, and availability service."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from app.catalog.repository import CatalogRepository
from app.catalog.schemas import (
    AvailabilityView,
    BranchView,
    ProductDetails,
    ProductOption,
    ProductSearchRequest,
    ProductSearchResponse,
    VariantSnapshot,
)
from app.config import get_config
from app.shared.errors import NotFoundError


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
    ) -> None:
        self._repository = repository
        self._product_images_dir = product_images_dir or get_config().product_images_dir
        self._image_url_cache: dict[str, str | None] = {}

    async def search(self, request: ProductSearchRequest) -> ProductSearchResponse:
        """Search and rank products using hard filters and semantic preferences.

        When relaxation is enabled and no result exists, the service relaxes
        color, branch, stock, and budget in that order. Every relaxation is
        returned explicitly so the agent cannot present alternatives as exact
        matches.
        """

        working = request.model_copy(update={"limit": max(request.limit, 20)})
        rows = await self._repository.search_rows(working)
        relaxed: list[str] = []

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

        products = [self._rank(self._with_resolved_image(row), request) for row in rows]
        products.sort(
            key=lambda item: (-item.match_score, -item.available_quantity, item.price)
        )
        products = products[: request.limit]
        return ProductSearchResponse(
            products=products,
            result_count=len(products),
            relaxed_constraints=relaxed,
        )

    async def get_product(self, product_id: int) -> ProductDetails:
        """Return product metadata and all active branch-specific options."""

        metadata = await self._repository.product_metadata(product_id)
        if not metadata:
            raise NotFoundError("Product was not found.", code="PRODUCT_NOT_FOUND")

        rows = await self._repository.search_rows(
            ProductSearchRequest(in_stock_only=False, allow_relaxation=False, limit=30),
            product_id=product_id,
            database_limit=300,
        )
        options = [
            self._rank(self._with_resolved_image(row), ProductSearchRequest())
            for row in rows
        ]
        options.sort(
            key=lambda item: (
                item.color.lower(),
                item.size,
                item.branch_name.lower(),
            )
        )
        metadata["image_urls"] = [
            url
            for url in (
                self._resolve_image_url(image_url)
                for image_url in await self._repository.image_urls(product_id)
            )
            if url is not None
        ]
        metadata["tags"] = metadata.get("tags") or []
        metadata["attributes"] = metadata.get("attributes") or {}
        return ProductDetails(**metadata, options=options)

    async def list_branches(self) -> list[BranchView]:
        """Return the active branches available for filtering and stock display."""

        return [BranchView(**row) for row in await self._repository.list_branches()]

    async def get_availability(
        self,
        variant_id: int,
        branch_id: int,
    ) -> AvailabilityView:
        """Return current sellable stock for an exact branch-specific variant."""

        row = await self._repository.availability_row(variant_id, branch_id)
        if not row:
            raise NotFoundError(
                "Product availability was not found.",
                code="AVAILABILITY_NOT_FOUND",
            )
        return AvailabilityView(
            product_id=row["product_id"],
            variant_id=row["variant_id"],
            branch_id=row["branch_id"],
            branch_code=row["branch_code"],
            branch_name=row["branch_name"],
            color=row["color"],
            size=row["size"],
            price=row["price"],
            available_quantity=max(int(row["available_quantity"] or 0), 0),
            in_transit_quantity=max(int(row["in_transit_quantity"] or 0), 0),
            is_available=int(row["available_quantity"] or 0) > 0,
        )

    async def variant_snapshot(
        self,
        variant_id: int,
        branch_id: int,
    ) -> VariantSnapshot:
        """Return trusted price and stock facts used by cart operations."""

        row = await self._repository.availability_row(variant_id, branch_id)
        if not row:
            raise NotFoundError("The selected variant was not found.", code="VARIANT_NOT_FOUND")
        return VariantSnapshot(
            product_id=row["product_id"],
            variant_id=row["variant_id"],
            branch_id=row["branch_id"],
            product_name=row["product_name"],
            article_code=row["article_code"],
            color=row["color"],
            size=row["size"],
            unit_price=row["price"],
            available_quantity=max(int(row["available_quantity"] or 0), 0),
            image_url=self._resolve_image_url(row.get("image_url")),
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

    @staticmethod
    def _rank(row: dict[str, Any], request: ProductSearchRequest) -> ProductOption:
        """Attach deterministic, explainable ranking metadata to a result."""

        item = deepcopy(row)
        tags = [str(tag) for tag in (item.get("tags") or [])]
        requested_tags = {tag.lower() for tag in request.semantic_tags}
        searchable_text = " ".join(
            str(item.get(field) or "")
            for field in (
                "product_name",
                "category",
                "description",
                "material",
                "fit",
                "season",
            )
        ).lower()
        matched_semantic_tags = {
            tag for tag in requested_tags if tag in searchable_text
        }
        score = 0.0
        reasons: list[str] = []

        if request.category:
            score += 25
            reasons.append("Category match")
        if request.sizes:
            score += 20
            reasons.append("Requested size")
        if request.branch_code:
            score += 20
            reasons.append("Preferred branch")
        if request.colors:
            score += 15
            reasons.append("Preferred color")
        if request.maximum_price is not None:
            score += 10
            reasons.append("Within budget")
        if matched_semantic_tags:
            score += min(20, len(matched_semantic_tags) * 5)
            reasons.append(
                "Matches " + ", ".join(sorted(matched_semantic_tags))
            )
        if int(item.get("available_quantity") or 0) > 0:
            score += 10
            reasons.append("In stock")

        item["tags"] = tags
        item["available_quantity"] = max(int(item.get("available_quantity") or 0), 0)
        item["in_transit_quantity"] = max(
            int(item.get("in_transit_quantity") or 0), 0
        )
        item["match_score"] = score
        item["match_reasons"] = reasons
        return ProductOption.model_validate(item)
