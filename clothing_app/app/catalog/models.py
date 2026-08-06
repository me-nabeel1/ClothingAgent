"""SQLAlchemy mappings for the existing ``clothing_store`` schema.

These models are read mappings for the demo APIs. The clothing application does
not create or modify catalog records.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

SCHEMA = "clothing_store"


class Branch(Base):
    """Physical branch that owns branch-specific stock."""

    __tablename__ = "branches"
    __table_args__ = (UniqueConstraint("branch_code"), {"schema": SCHEMA})

    branch_id: Mapped[int] = mapped_column(primary_key=True)
    branch_code: Mapped[str] = mapped_column(String(30), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Category(Base):
    """Hierarchical clothing category."""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("category_code"), {"schema": SCHEMA})

    category_id: Mapped[int] = mapped_column(primary_key=True)
    parent_category_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.categories.category_id", ondelete="RESTRICT")
    )
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_code: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    parent: Mapped[Category | None] = relationship(remote_side=[category_id])


class Color(Base):
    """Reusable product color."""

    __tablename__ = "colors"
    __table_args__ = (UniqueConstraint("color_code"), {"schema": SCHEMA})

    color_id: Mapped[int] = mapped_column(primary_key=True)
    color_name: Mapped[str] = mapped_column(String(60), nullable=False)
    color_code: Mapped[str] = mapped_column(String(40), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)


class Size(Base):
    """Reusable clothing size."""

    __tablename__ = "sizes"
    __table_args__ = (
        UniqueConstraint("size_label", "size_type"),
        {"schema": SCHEMA},
    )

    size_id: Mapped[int] = mapped_column(primary_key=True)
    size_label: Mapped[str] = mapped_column(String(20), nullable=False)
    size_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class Product(Base):
    """Clothing article independent of color, size, and branch."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("article_code"),
        Index("ix_products_category_status", "category_id", "product_status"),
        {"schema": SCHEMA},
    )

    product_id: Mapped[int] = mapped_column(primary_key=True)
    article_code: Mapped[str] = mapped_column(String(40), nullable=False)
    product_name: Mapped[str] = mapped_column(String(180), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.categories.category_id", ondelete="RESTRICT"),
        nullable=False,
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    material: Mapped[str | None] = mapped_column(String(160))
    fit: Mapped[str | None] = mapped_column(String(60))
    season: Mapped[str | None] = mapped_column(String(80))
    base_cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    base_selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    product_status: Mapped[str] = mapped_column(String(30), nullable=False)
    availability_scope: Mapped[str] = mapped_column(String(40), nullable=False)
    launch_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    category: Mapped[Category] = relationship()


class ProductVariant(Base):
    """Exact sellable color and size combination."""

    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("product_id", "color_id", "size_id"),
        UniqueConstraint("sku"),
        UniqueConstraint("barcode"),
        Index("ix_variants_product_active", "product_id", "is_active"),
        {"schema": SCHEMA},
    )

    variant_id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    color_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.colors.color_id", ondelete="RESTRICT"),
        nullable=False,
    )
    size_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.sizes.size_id", ondelete="RESTRICT"),
        nullable=False,
    )
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    barcode: Mapped[str] = mapped_column(String(30), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ProductImage(Base):
    """Product image metadata."""

    __tablename__ = "product_images"
    __table_args__ = (
        Index("ix_product_images_primary", "product_id", "is_primary"),
        {"schema": SCHEMA},
    )

    image_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(250))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)


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
