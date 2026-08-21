"""Inventory availability service."""
from app.inventory.repository import InventoryRepository
from app.inventory.schemas import AvailabilityView, VariantSnapshot
from app.common.exceptions import NotFoundError


class InventoryService:
    """Expose authoritative branch inventory through a small semantic service."""

    def __init__(self, repository: InventoryRepository) -> None:
        self._repository = repository

    async def get_availability(self, variant_id: int, branch_id: int) -> AvailabilityView:
        """Return current sellable availability for one exact variant and branch."""
        row = await self._repository.availability_row(variant_id, branch_id)
        if not row:
            raise NotFoundError("Product availability was not found.", code="AVAILABILITY_NOT_FOUND")
        return AvailabilityView(
            product_id=row["product_id"],
            category_id=row.get("category_id"),
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

    async def variant_snapshot(self, variant_id: int, branch_id: int) -> VariantSnapshot:
        """Return trusted sellable product facts for cart/order operations."""
        row = await self._repository.availability_row(variant_id, branch_id)
        if not row:
            raise NotFoundError("The selected variant was not found.", code="VARIANT_NOT_FOUND")
        return VariantSnapshot(
            product_id=row["product_id"],
            category_id=row.get("category_id"),
            variant_id=row["variant_id"],
            branch_id=row["branch_id"],
            product_name=row["product_name"],
            article_code=row["article_code"],
            color=row["color"],
            size=row["size"],
            unit_price=row["price"],
            available_quantity=max(int(row["available_quantity"] or 0), 0),
            image_url=row.get("image_url"),
        )
