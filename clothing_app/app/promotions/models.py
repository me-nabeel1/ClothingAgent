"""SQLAlchemy mappings for promotions and discounts."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

SCHEMA = "clothing_store"

class Offer(Base):
    """Data-driven promotional offers."""

    __tablename__ = "offers"
    __table_args__ = {"schema": SCHEMA}

    offer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    offer_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    offer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # discount details
    discount_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    benefit_type: Mapped[str] = mapped_column(String(30), nullable=False) # PERCENTAGE, FIXED, FREE_DELIVERY
    
    # conditions
    min_cart_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    min_quantity: Mapped[int | None] = mapped_column(Integer)
    
    # targets
    target_branch_id: Mapped[int | None] = mapped_column(Integer)
    target_category_id: Mapped[int | None] = mapped_column(Integer)
    target_product_id: Mapped[int | None] = mapped_column(Integer)
    target_variant_id: Mapped[int | None] = mapped_column(Integer)
    target_scope: Mapped[str] = mapped_column(String(30), nullable=False) # STORE_WIDE, BRANCH, CATEGORY, PRODUCT, VARIANT
    
    # validity
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # logic
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stacking_policy: Mapped[str] = mapped_column(String(30), nullable=False, default="EXCLUSIVE")
