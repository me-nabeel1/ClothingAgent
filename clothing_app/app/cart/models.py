"""SQLAlchemy mappings for persistent cart."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

SCHEMA = "clothing_store"

class Cart(Base):
    __tablename__ = "carts"
    __table_args__ = {"schema": SCHEMA}

    cart_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(120), nullable=False)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan", lazy="selectin")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "variant_id", "branch_id"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
        {"schema": SCHEMA}
    )

    item_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    cart_id: Mapped[UUID] = mapped_column(ForeignKey(f"{SCHEMA}.carts.cart_id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="items")
