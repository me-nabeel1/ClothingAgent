"""Common shared enumerations."""
from enum import Enum

class OrderStatus(str, Enum):
    PLACED = "PLACED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class BenefitType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"
    FREE_DELIVERY = "FREE_DELIVERY"

class TargetScope(str, Enum):
    STORE_WIDE = "STORE_WIDE"
    BRANCH = "BRANCH"
    CATEGORY = "CATEGORY"
    PRODUCT = "PRODUCT"
    VARIANT = "VARIANT"

class StackingPolicy(str, Enum):
    EXCLUSIVE = "EXCLUSIVE"
    STACKABLE = "STACKABLE"
