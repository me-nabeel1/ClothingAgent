"""SQLAlchemy mappings for the Northstar commerce catalog."""
from __future__ import annotations
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

SCHEMA = "clothing_store"


class Store(Base):
    """Top-level tenant for catalog and branch data."""
    __tablename__ = "stores"
    __table_args__ = {"schema": SCHEMA}
    store_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    store_name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Branch(Base):
    """Physical branch belonging to one store."""
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("store_id", "branch_code"),
        {"schema": SCHEMA},
    )
    branch_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
    branch_code: Mapped[str] = mapped_column(String(30), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Category(Base):
    """Hierarchical category owned by one store."""
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("store_id", "category_code"),
        {"schema": SCHEMA},
    )
    category_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
    parent_category_id: Mapped[int | None] = mapped_column(ForeignKey(f"{SCHEMA}.categories.category_id", ondelete="RESTRICT"))
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_code: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    parent: Mapped["Category | None"] = relationship(remote_side=[category_id])


class Color(Base):
    """Reusable color vocabulary shared by the catalog."""
    __tablename__ = "colors"
    __table_args__ = (UniqueConstraint("color_code"), {"schema": SCHEMA})
    color_id: Mapped[int] = mapped_column(primary_key=True)
    color_name: Mapped[str] = mapped_column(String(60), nullable=False)
    color_code: Mapped[str] = mapped_column(String(40), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(7), nullable=False)


class Size(Base):
    """Reusable size vocabulary shared by the catalog."""
    __tablename__ = "sizes"
    __table_args__ = (UniqueConstraint("size_label", "size_type"), {"schema": SCHEMA})
    size_id: Mapped[int] = mapped_column(primary_key=True)
    size_label: Mapped[str] = mapped_column(String(20), nullable=False)
    size_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class Product(Base):
    """Store-scoped clothing article independent of color, size, and branch."""
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("store_id", "article_code"),
        Index("ix_products_store_category_status", "store_id", "category_id", "product_status"),
        {"schema": SCHEMA},
    )
    product_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
    article_code: Mapped[str] = mapped_column(String(40), nullable=False)
    product_name: Mapped[str] = mapped_column(String(180), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.categories.category_id", ondelete="RESTRICT"), nullable=False)
    product_type: Mapped[str] = mapped_column(String(60), nullable=False)
    occasion: Mapped[str | None] = mapped_column(String(60))
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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    category: Mapped[Category] = relationship()


class ProductVariant(Base):
    """Store-scoped sellable color and size combination."""
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("store_id", "sku"),
        UniqueConstraint("product_id", "color_id", "size_id"),
        UniqueConstraint("barcode"),
        Index("ix_variants_store_product_active", "store_id", "product_id", "is_active"),
        {"schema": SCHEMA},
    )
    variant_id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.products.product_id", ondelete="CASCADE"), nullable=False)
    color_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.colors.color_id", ondelete="RESTRICT"), nullable=False)
    size_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.sizes.size_id", ondelete="RESTRICT"), nullable=False)
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    barcode: Mapped[str] = mapped_column(String(30), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class ProductImage(Base):
    """Product image metadata."""
    __tablename__ = "product_images"
    __table_args__ = (Index("ix_product_images_primary", "product_id", "is_primary"), {"schema": SCHEMA})
    image_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.products.product_id", ondelete="CASCADE"), nullable=False)
    color_id: Mapped[int | None] = mapped_column(ForeignKey(f"{SCHEMA}.colors.color_id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(250))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
