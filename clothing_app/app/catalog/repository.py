"""SQLAlchemy retrieval queries for catalog and inventory data."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.catalog.models import (
    Branch,
    BranchInventory,
    Category,
    Color,
    Product,
    ProductImage,
    ProductVariant,
    Size,
)
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
            Product.gender.in_(["MEN", "UNISEX"]),
        ]
        if product_id is not None:
            conditions.append(Product.product_id == product_id)
        if request.categories:
            matching_categories = []
            parent = aliased(Category)
            for category in request.categories:
                category_term = category.strip().lower()
                conditions_for_category = [
                    func.lower(Category.category_name).contains(category_term),
                    func.lower(Category.category_code).contains(category_term),
                    func.lower(parent.category_name).contains(category_term),
                ]
                if category_term in ("pants", "trouser", "trousers"):
                    conditions_for_category.extend([
                        func.lower(Category.category_name).contains("pants"),
                        func.lower(Category.category_name).contains("trouser"),
                    ])
                    
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
        if request.sizes:
            conditions.append(Size.size_label.in_(request.sizes))
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
                request.sizes,
                request.minimum_price is not None,
                request.maximum_price is not None,
                request.branch_code,
                request.materials,
                request.fits,
            )
        )
        if request.query_text and not request.semantic_tags and not structured_filters_present:
            terms = [
                token
                for token in re.findall(r"[a-zA-Z0-9-]+", request.query_text.lower())
                if len(token) >= 3
                and token not in {"show", "find", "need", "want", "with", "please"}
            ][:8]
            if terms:
                searchable_columns = (
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
                            column.ilike(f"%{term}%")
                            for term in terms
                            for column in searchable_columns
                        ]
                    )
                )

        available = self._available_quantity_expression()
        if request.in_stock_only:
            conditions.append(available > 0)

        result = await self._db.execute(
            self._base_statement()
            .where(and_(*conditions))
            .order_by(available.desc(), ProductVariant.selling_price.asc())
            .limit(database_limit)
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
                Product.gender.in_(["MEN", "UNISEX"])
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
                Product.gender.in_(["MEN", "UNISEX"]),
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
                Product.product_name.label("product_name"),
                Category.category_name.label("category"),
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
