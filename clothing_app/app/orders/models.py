"""SQLAlchemy mappings for transactional orders."""
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey, Uuid, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

SCHEMA = "clothing_store"

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = {"schema": SCHEMA}

    order_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(120), nullable=False)
    store_id: Mapped[str] = mapped_column(String(50), nullable=False)
    
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PLACED")
    
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    applied_offer_code: Mapped[str | None] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan", lazy="selectin")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": SCHEMA}

    item_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    order_id: Mapped[UUID] = mapped_column(ForeignKey(f"{SCHEMA}.orders.order_id", ondelete="CASCADE"), nullable=False)
    
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    branch_id: Mapped[int] = mapped_column(Integer, nullable=False)
    
    article_code: Mapped[str] = mapped_column(String(80), nullable=False)
    product_name: Mapped[str] = mapped_column(String(180), nullable=False)
    color: Mapped[str] = mapped_column(String(60), nullable=False)
    size: Mapped[str] = mapped_column(String(30), nullable=False)
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    order: Mapped["Order"] = relationship(back_populates="items")
