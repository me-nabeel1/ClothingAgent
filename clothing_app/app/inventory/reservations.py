"""TTL inventory reservation primitives used by carts.

The reservation model is intentionally lightweight for V1: reservations are stored
in PostgreSQL, inventory rows remain authoritative, and expired reservations are
released lazily on cart mutations/checkout. A later worker can move expiry cleanup
out of request paths without changing the contract.
"""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.inventory.models import BranchInventory
from app.common.exceptions import ConflictError

SCHEMA = "clothing_store"


class InventoryReservation(Base):
    """One cart's temporary hold on inventory for a branch-specific variant."""
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        UniqueConstraint("cart_id", "variant_id", "branch_id"),
        {"schema": SCHEMA},
    )
    reservation_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    cart_id: Mapped[UUID] = mapped_column(ForeignKey(f"{SCHEMA}.carts.cart_id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")


class ReservationService:
    """Maintain short-lived inventory holds and release them safely."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def release_expired(self) -> None:
        """Release expired active reservations and return stock to availability."""
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(InventoryReservation).where(
                InventoryReservation.status == "ACTIVE",
                InventoryReservation.expires_at <= now,
            )
        )
        for reservation in result.scalars().all():
            await self._release_one(reservation)
        await self._db.flush()

    async def reserve(self, cart_id: UUID, variant_id: int, branch_id: int, quantity: int, expires_at: datetime) -> None:
        """Increase the branch inventory hold for one cart item."""
        await self.release_expired()
        result = await self._db.execute(
            select(BranchInventory).where(
                BranchInventory.variant_id == variant_id,
                BranchInventory.branch_id == branch_id,
            ).with_for_update()
        )
        inventory = result.scalars().first()
        if not inventory:
            raise ConflictError("Inventory record not found.", code="INVENTORY_NOT_FOUND")

        existing_result = await self._db.execute(
            select(InventoryReservation).where(
                InventoryReservation.cart_id == cart_id,
                InventoryReservation.variant_id == variant_id,
                InventoryReservation.branch_id == branch_id,
                InventoryReservation.status == "ACTIVE",
            ).with_for_update()
        )
        existing = existing_result.scalars().first()
        additional = quantity
        if existing:
            additional += existing.quantity

        available = inventory.quantity_on_hand - inventory.reserved_quantity - inventory.damaged_quantity
        if available < quantity:
            raise ConflictError("The requested quantity is no longer available.", code="OUT_OF_STOCK")

        inventory.reserved_quantity += quantity
        if existing:
            existing.quantity = additional
            existing.expires_at = expires_at
        else:
            self._db.add(InventoryReservation(
                reservation_id=uuid4(), cart_id=cart_id, variant_id=variant_id,
                branch_id=branch_id, quantity=quantity, expires_at=expires_at, status="ACTIVE",
            ))
        await self._db.flush()

    async def release_for_item(self, cart_id: UUID, variant_id: int, branch_id: int) -> None:
        """Release one cart item's active inventory hold."""
        result = await self._db.execute(
            select(InventoryReservation).where(
                InventoryReservation.cart_id == cart_id,
                InventoryReservation.variant_id == variant_id,
                InventoryReservation.branch_id == branch_id,
                InventoryReservation.status == "ACTIVE",
            ).with_for_update()
        )
        reservation = result.scalars().first()
        if reservation:
            await self._release_one(reservation)
            await self._db.flush()

    async def release_for_cart(self, cart_id: UUID) -> None:
        """Release all active reservations belonging to a cart."""
        result = await self._db.execute(
            select(InventoryReservation).where(
                InventoryReservation.cart_id == cart_id,
                InventoryReservation.status == "ACTIVE",
            ).with_for_update()
        )
        for reservation in result.scalars().all():
            await self._release_one(reservation)
        await self._db.flush()

    async def consume_for_order(self, cart_id: UUID) -> set[tuple[int, int]]:
        """Convert active reservations into stock deductions and return consumed keys."""
        consumed: set[tuple[int, int]] = set()
        result = await self._db.execute(
            select(InventoryReservation).where(
                InventoryReservation.cart_id == cart_id,
                InventoryReservation.status == "ACTIVE",
            ).with_for_update()
        )
        for reservation in result.scalars().all():
            inv_result = await self._db.execute(
                select(BranchInventory).where(
                    BranchInventory.variant_id == reservation.variant_id,
                    BranchInventory.branch_id == reservation.branch_id,
                ).with_for_update()
            )
            inventory = inv_result.scalars().first()
            if not inventory:
                raise ConflictError("Inventory record not found.", code="INVENTORY_NOT_FOUND")
            if inventory.reserved_quantity < reservation.quantity:
                raise ConflictError("Inventory reservation is inconsistent.", code="RESERVATION_INVALID")
            inventory.quantity_on_hand -= reservation.quantity
            inventory.reserved_quantity -= reservation.quantity
            reservation.status = "CONSUMED"
            consumed.add((reservation.variant_id, reservation.branch_id))
        await self._db.flush()
        return consumed

    async def _release_one(self, reservation: InventoryReservation) -> None:
        """Release one reservation's quantity from the inventory aggregate."""
        inv_result = await self._db.execute(
            select(BranchInventory).where(
                BranchInventory.variant_id == reservation.variant_id,
                BranchInventory.branch_id == reservation.branch_id,
            ).with_for_update()
        )
        inventory = inv_result.scalars().first()
        if inventory:
            inventory.reserved_quantity = max(0, inventory.reserved_quantity - reservation.quantity)
        reservation.status = "RELEASED"
