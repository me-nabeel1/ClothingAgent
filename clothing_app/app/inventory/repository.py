"""SQLAlchemy retrieval for inventory data."""
from typing import Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.catalog.models import Product, ProductVariant, Branch
from app.inventory.models import BranchInventory
from app.config import get_config

class InventoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def availability_row(self, variant_id: int, branch_id: int) -> dict[str, Any] | None:
        """Return availability for one exact variant and branch."""
        available = (
            BranchInventory.quantity_on_hand
            - BranchInventory.reserved_quantity
            - BranchInventory.damaged_quantity
        )
        result = await self._db.execute(
            select(
                Product.product_id,
                Product.category_id,
                ProductVariant.variant_id,
                Branch.branch_id,
                Branch.branch_code,
                Branch.branch_name,
                Product.article_code,
                Product.product_name,
                ProductVariant.selling_price.label("price"),
                available.label("available_quantity"),
                BranchInventory.in_transit_quantity,
            )
            .select_from(ProductVariant)
            .join(Product, Product.product_id == ProductVariant.product_id)
            .join(BranchInventory, BranchInventory.variant_id == ProductVariant.variant_id)
            .join(Branch, Branch.branch_id == BranchInventory.branch_id)
            .where(
                ProductVariant.variant_id == variant_id,
                Branch.branch_id == branch_id,
                Product.store_id == get_config().store_id,
                Branch.store_id == get_config().store_id,
                ProductVariant.store_id == get_config().store_id,
                Product.product_status == "ACTIVE",
                ProductVariant.is_active.is_(True),
                Branch.is_active.is_(True),
            )
            .limit(1)
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_stock(self, variant_id: int, branch_id: int) -> int:
        row = await self.availability_row(variant_id, branch_id)
        if row:
            return max(int(row["available_quantity"] or 0), 0)
        return 0
