"""SQLAlchemy mappings for inventory."""
from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

SCHEMA = "clothing_store"

class BranchInventory(Base):
    """Stock snapshot for one variant in one branch."""

    __tablename__ = "branch_inventory"
    __table_args__ = (
        UniqueConstraint("branch_id", "variant_id"),
        Index("ix_inventory_variant_branch", "variant_id", "branch_id"),
        {"schema": SCHEMA},
    )

    inventory_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.branches.branch_id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.product_variants.variant_id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    damaged_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    in_transit_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock_level: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
