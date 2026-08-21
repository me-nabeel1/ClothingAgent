"""SQLAlchemy mappings for promotions and discounts."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

SCHEMA = "clothing_store"

class Offer(Base):
    """Data-driven promotional offers."""

    __tablename__ = "offers"
    __table_args__ = (
        CheckConstraint("discount_percentage IS NULL OR discount_percentage >= 0", name="non_negative_discount_percentage"),
        CheckConstraint("discount_amount IS NULL OR discount_amount >= 0", name="non_negative_discount_amount"),
        CheckConstraint("min_cart_value IS NULL OR min_cart_value >= 0", name="non_negative_min_cart_value"),
        CheckConstraint("min_quantity IS NULL OR min_quantity > 0", name="positive_min_quantity"),
        CheckConstraint("valid_until IS NULL OR valid_until > valid_from", name="valid_offer_window"),
        {"schema": SCHEMA},
    )

    offer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.stores.store_id", ondelete="CASCADE"), nullable=False, default="northstar")
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
