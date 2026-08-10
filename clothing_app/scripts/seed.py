"""Database seeder for the Northstar Menswear demo store."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_db
from app.catalog.models import Branch, Category, Product, ProductVariant, Color, Size, ProductImage
from app.inventory.models import BranchInventory
from app.promotions.models import Offer

async def seed_db(db: AsyncSession):
    # clear tables
    await db.execute(text("TRUNCATE TABLE clothing_store.branches CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.categories CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.colors CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.sizes CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.offers CASCADE"))
    
    b1 = Branch(branch_code="NS-NY", branch_name="Northstar New York", city="New York", address="5th Ave", is_active=True, created_at=datetime.now(timezone.utc))
    b2 = Branch(branch_code="NS-LA", branch_name="Northstar Los Angeles", city="Los Angeles", address="Rodeo Drive", is_active=True, created_at=datetime.now(timezone.utc))
    b3 = Branch(branch_code="NS-CH", branch_name="Northstar Chicago", city="Chicago", address="Michigan Ave", is_active=True, created_at=datetime.now(timezone.utc))
    db.add_all([b1, b2, b3])
    await db.flush()
    
    cat_shirts = Category(category_name="Shirts", category_code="SHIRTS", is_active=True)
    cat_pants = Category(category_name="Pants", category_code="PANTS", is_active=True)
    cat_jackets = Category(category_name="Jackets", category_code="JACKETS", is_active=True)
    db.add_all([cat_shirts, cat_pants, cat_jackets])
    await db.flush()
    
    col_navy = Color(color_name="Navy", color_code="NVY", hex_code="#000080")
    col_white = Color(color_name="White", color_code="WHT", hex_code="#FFFFFF")
    col_black = Color(color_name="Black", color_code="BLK", hex_code="#000000")
    col_olive = Color(color_name="Olive", color_code="OLV", hex_code="#808000")
    db.add_all([col_navy, col_white, col_black, col_olive])
    await db.flush()
    
    sizes = []
    sort_order = 1
    for s in ["S", "M", "L", "XL", "30", "32", "34", "36"]:
        size = Size(size_label=s, size_type="standard", sort_order=sort_order)
        sort_order += 1
        sizes.append(size)
        db.add(size)
    await db.flush()
    s_s, s_m, s_l, s_xl, s_30, s_32, s_34, s_36 = sizes
    
    p1 = Product(article_code="NS-SH-001", product_name="Premium Oxford Shirt", category_id=cat_shirts.category_id, product_status="ACTIVE", gender="M", brand="Northstar", material="Cotton", fit="Slim", season="All Season", base_cost_price=Decimal("20.00"), base_selling_price=Decimal("59.99"), availability_scope="STORE_WIDE")
    p2 = Product(article_code="NS-PA-001", product_name="Everyday Chinos", category_id=cat_pants.category_id, product_status="ACTIVE", gender="M", brand="Northstar", material="Cotton Blend", fit="Regular", season="All Season", base_cost_price=Decimal("15.00"), base_selling_price=Decimal("49.99"), availability_scope="STORE_WIDE")
    p3 = Product(article_code="NS-JA-001", product_name="Lightweight Bomber Jacket", category_id=cat_jackets.category_id, product_status="ACTIVE", gender="M", brand="Northstar", material="Polyester", fit="Regular", season="Winter", base_cost_price=Decimal("40.00"), base_selling_price=Decimal("89.99"), availability_scope="STORE_WIDE")
    p4 = Product(article_code="NS-SH-002", product_name="Casual Linen Shirt", category_id=cat_shirts.category_id, product_status="ACTIVE", gender="M", brand="Northstar", material="Linen", fit="Relaxed", season="Summer", base_cost_price=Decimal("15.00"), base_selling_price=Decimal("45.99"), availability_scope="STORE_WIDE")
    db.add_all([p1, p2, p3, p4])
    await db.flush()
    
    variants = []
    # Oxford Shirt Variants
    v1 = ProductVariant(product_id=p1.product_id, color_id=col_white.color_id, size_id=s_m.size_id, sku="NS-SH-001-W-M", barcode="001WM", cost_price=Decimal("20.00"), selling_price=Decimal("59.99"), is_active=True)
    v2 = ProductVariant(product_id=p1.product_id, color_id=col_white.color_id, size_id=s_l.size_id, sku="NS-SH-001-W-L", barcode="001WL", cost_price=Decimal("20.00"), selling_price=Decimal("59.99"), is_active=True)
    v3 = ProductVariant(product_id=p1.product_id, color_id=col_navy.color_id, size_id=s_m.size_id, sku="NS-SH-001-N-M", barcode="001NM", cost_price=Decimal("20.00"), selling_price=Decimal("59.99"), is_active=True)
    
    # Everyday Chinos Variants
    v4 = ProductVariant(product_id=p2.product_id, color_id=col_navy.color_id, size_id=s_32.size_id, sku="NS-PA-001-N-32", barcode="PA001N32", cost_price=Decimal("15.00"), selling_price=Decimal("49.99"), is_active=True)
    v5 = ProductVariant(product_id=p2.product_id, color_id=col_olive.color_id, size_id=s_34.size_id, sku="NS-PA-001-O-34", barcode="PA001O34", cost_price=Decimal("15.00"), selling_price=Decimal("49.99"), is_active=True)
    
    # Bomber Jacket Variant
    v6 = ProductVariant(product_id=p3.product_id, color_id=col_black.color_id, size_id=s_l.size_id, sku="NS-JA-001-B-L", barcode="JA001BL", cost_price=Decimal("40.00"), selling_price=Decimal("89.99"), is_active=True)
    
    # Casual Linen Shirt Variant (Out of stock testing)
    v7 = ProductVariant(product_id=p4.product_id, color_id=col_white.color_id, size_id=s_l.size_id, sku="NS-SH-002-W-L", barcode="SH002WL", cost_price=Decimal("15.00"), selling_price=Decimal("45.99"), is_active=True)
    
    variants.extend([v1, v2, v3, v4, v5, v6, v7])
    db.add_all(variants)
    await db.flush()
    
    # Inventory
    inventories = [
        # NY Branch
        BranchInventory(variant_id=v1.variant_id, branch_id=b1.branch_id, quantity_on_hand=50, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v2.variant_id, branch_id=b1.branch_id, quantity_on_hand=30, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v3.variant_id, branch_id=b1.branch_id, quantity_on_hand=20, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v4.variant_id, branch_id=b1.branch_id, quantity_on_hand=15, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v6.variant_id, branch_id=b1.branch_id, quantity_on_hand=5, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v7.variant_id, branch_id=b1.branch_id, quantity_on_hand=0, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        
        # LA Branch
        BranchInventory(variant_id=v1.variant_id, branch_id=b2.branch_id, quantity_on_hand=0, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v2.variant_id, branch_id=b2.branch_id, quantity_on_hand=10, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v5.variant_id, branch_id=b2.branch_id, quantity_on_hand=25, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v7.variant_id, branch_id=b2.branch_id, quantity_on_hand=5, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        
        # CH Branch
        BranchInventory(variant_id=v1.variant_id, branch_id=b3.branch_id, quantity_on_hand=5, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
        BranchInventory(variant_id=v6.variant_id, branch_id=b3.branch_id, quantity_on_hand=2, reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=10, updated_at=datetime.now(timezone.utc)),
    ]
    db.add_all(inventories)
    
    # Promotions
    off1 = Offer(offer_code="WELCOME10", offer_name="Welcome 10% Off", description="10% off on all items for new customers", discount_percentage=Decimal("10.00"), benefit_type="PERCENTAGE", target_scope="STORE_WIDE", valid_from=datetime.now(timezone.utc), is_active=True, priority=1)
    off2 = Offer(offer_code="SAVE20", offer_name="Flat $20 Off", description="$20 off on orders above $100", discount_amount=Decimal("20.00"), benefit_type="FIXED", target_scope="STORE_WIDE", min_cart_value=Decimal("100.00"), valid_from=datetime.now(timezone.utc), is_active=True, priority=2)
    db.add_all([off1, off2])
    
    await db.commit()
    print("Database seeded successfully with realistic Northstar Menswear data!")

async def main():
    async for db in get_db():
        await seed_db(db)
        break 

if __name__ == "__main__":
    asyncio.run(main())
