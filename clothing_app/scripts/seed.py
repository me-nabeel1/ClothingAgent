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
    # Truncate
    await db.execute(text("TRUNCATE TABLE clothing_store.branches CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.categories CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.colors CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.sizes CASCADE"))
    await db.execute(text("TRUNCATE TABLE clothing_store.offers CASCADE"))
    
    now = datetime.now(timezone.utc)
    
    # 1. Branches
    b1 = Branch(branch_code="ISB-F7", branch_name="Northstar F-7", city="Islamabad", address="F-7 Markaz", is_active=True, created_at=now)
    b2 = Branch(branch_code="ISB-GG", branch_name="Northstar Gulberg Greens", city="Islamabad", address="Gulberg", is_active=True, created_at=now)
    b3 = Branch(branch_code="LHR-MR", branch_name="Northstar Mall Road", city="Lahore", address="Mall Road", is_active=True, created_at=now)
    db.add_all([b1, b2, b3])
    await db.flush()

    # 2. Categories
    c_shirts = Category(category_name="Shirts", category_code="SHIRTS", is_active=True)
    c_tshirts = Category(category_name="T-Shirts", category_code="TSHIRTS", is_active=True)
    c_pants = Category(category_name="Pants", category_code="PANTS", is_active=True)
    c_trad = Category(category_name="Traditional", category_code="TRADITIONAL", is_active=True)
    c_outer = Category(category_name="Outerwear", category_code="OUTERWEAR", is_active=True)
    c_formal = Category(category_name="Formal Wear", category_code="FORMAL", is_active=True)
    db.add_all([c_shirts, c_tshirts, c_pants, c_trad, c_outer, c_formal])
    await db.flush()

    # 3. Colors
    colors = {
        "Black": Color(color_name="Black", color_code="BLK", hex_code="#000000"),
        "White": Color(color_name="White", color_code="WHT", hex_code="#FFFFFF"),
        "Navy": Color(color_name="Navy", color_code="NVY", hex_code="#000080"),
        "Blue": Color(color_name="Blue", color_code="BLU", hex_code="#0000FF"),
        "Grey": Color(color_name="Grey", color_code="GRY", hex_code="#808080"),
        "Olive": Color(color_name="Olive", color_code="OLV", hex_code="#808000"),
        "Maroon": Color(color_name="Maroon", color_code="MRN", hex_code="#800000"),
        "Beige": Color(color_name="Beige", color_code="BGE", hex_code="#F5F5DC"),
        "Brown": Color(color_name="Brown", color_code="BRN", hex_code="#A52A2A"),
    }
    db.add_all(colors.values())
    await db.flush()

    # 4. Sizes
    sizes = {}
    for i, s in enumerate(["S", "M", "L", "XL", "XXL", "30", "32", "34", "36", "38"]):
        sz = Size(size_label=s, size_type="standard", sort_order=i+1)
        sizes[s] = sz
        db.add(sz)
    await db.flush()

    # 5. Products
    products = []
    
    # Case A: Available - Premium Oxford Shirt
    p1 = Product(article_code="NS-SH-001", product_name="Premium Oxford Shirt", category_id=c_shirts.category_id, product_type="shirt", occasion="formal", gender="MEN", brand="Northstar", material="Cotton", fit="Slim", season="All Season", base_cost_price=Decimal("1500"), base_selling_price=Decimal("4500"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    
    # Case B/C: Out of stock / Branch difference - Casual Linen Shirt
    p2 = Product(article_code="NS-SH-002", product_name="Casual Linen Shirt", category_id=c_shirts.category_id, product_type="shirt", occasion="casual", gender="MEN", brand="Northstar", material="Linen", fit="Relaxed", season="Summer", base_cost_price=Decimal("1200"), base_selling_price=Decimal("3500"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    
    # Case I: Occasion Mismatch (Wedding Kurta)
    p3 = Product(article_code="NS-TR-001", product_name="Embroidered Wedding Kurta", category_id=c_trad.category_id, product_type="kurta", occasion="wedding", gender="MEN", brand="Northstar", material="Silk Blend", fit="Regular", season="All Season", base_cost_price=Decimal("4000"), base_selling_price=Decimal("9500"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    
    # Additional products for depth
    p4 = Product(article_code="NS-TS-001", product_name="Basic Crew Neck T-Shirt", category_id=c_tshirts.category_id, product_type="t_shirt", occasion="casual", gender="MEN", brand="Northstar", material="Cotton", fit="Regular", season="Summer", base_cost_price=Decimal("500"), base_selling_price=Decimal("1500"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    p5 = Product(article_code="NS-PA-001", product_name="Everyday Chinos", category_id=c_pants.category_id, product_type="chino", occasion="casual", gender="MEN", brand="Northstar", material="Cotton Blend", fit="Slim", season="All Season", base_cost_price=Decimal("1800"), base_selling_price=Decimal("4500"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    p6 = Product(article_code="NS-JA-001", product_name="Classic Bomber Jacket", category_id=c_outer.category_id, product_type="bomber_jacket", occasion="casual", gender="MEN", brand="Northstar", material="Polyester", fit="Regular", season="Winter", base_cost_price=Decimal("4500"), base_selling_price=Decimal("11000"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    p7 = Product(article_code="NS-FW-001", product_name="Executive Two-Piece Suit", category_id=c_formal.category_id, product_type="suit", occasion="business", gender="MEN", brand="Northstar", material="Wool Blend", fit="Tailored", season="Winter", base_cost_price=Decimal("8000"), base_selling_price=Decimal("18000"), availability_scope="STORE_WIDE", product_status="ACTIVE")
    p8 = Product(article_code="NS-PA-002", product_name="Denim Jeans", category_id=c_pants.category_id, product_type="jeans", occasion="casual", gender="MEN", brand="Northstar", material="Denim", fit="Straight", season="All Season", base_cost_price=Decimal("2000"), base_selling_price=Decimal("5000"), availability_scope="STORE_WIDE", product_status="ACTIVE")

    db.add_all([p1, p2, p3, p4, p5, p6, p7, p8])
    await db.flush()

    # 6. Variants and Inventory
    def create_variant(prod, col, sz, is_active=True):
        return ProductVariant(
            product_id=prod.product_id,
            color_id=colors[col].color_id,
            size_id=sizes[sz].size_id,
            sku=f"{prod.article_code}-{col[:1].upper()}-{sz}",
            barcode=f"{prod.article_code.replace('-','')}{col[:1].upper()}{sz}",
            cost_price=prod.base_cost_price,
            selling_price=prod.base_selling_price,
            is_active=is_active
        )
        
    def add_inv(v, b, qty):
        db.add(BranchInventory(
            variant_id=v.variant_id, branch_id=b.branch_id, 
            quantity_on_hand=qty, reserved_quantity=0, damaged_quantity=0, 
            in_transit_quantity=0, reorder_level=5, updated_at=now
        ))

    # P1 Variants
    v_p1_blk_m = create_variant(p1, "Black", "M")
    v_p1_blk_l = create_variant(p1, "Black", "L")
    v_p1_wht_l = create_variant(p1, "White", "L")
    db.add_all([v_p1_blk_m, v_p1_blk_l, v_p1_wht_l])
    await db.flush()
    # P1 Inventory
    add_inv(v_p1_blk_m, b1, 10); add_inv(v_p1_blk_m, b2, 5); add_inv(v_p1_blk_m, b3, 0)
    add_inv(v_p1_blk_l, b1, 15); add_inv(v_p1_blk_l, b2, 10); add_inv(v_p1_blk_l, b3, 20)
    add_inv(v_p1_wht_l, b1, 5); add_inv(v_p1_wht_l, b2, 0); add_inv(v_p1_wht_l, b3, 0)

    # P2 Variants (Linen shirt - test branch difference)
    v_p2_wht_l = create_variant(p2, "White", "L")
    v_p2_nvy_m = create_variant(p2, "Navy", "M")
    db.add_all([v_p2_wht_l, v_p2_nvy_m])
    await db.flush()
    # P2 Inventory: WHT-L is Out of stock in ISB-F7 (b1), but available in LHR-MR (b3)
    add_inv(v_p2_wht_l, b1, 0); add_inv(v_p2_wht_l, b2, 0); add_inv(v_p2_wht_l, b3, 10)
    add_inv(v_p2_nvy_m, b1, 20); add_inv(v_p2_nvy_m, b2, 20); add_inv(v_p2_nvy_m, b3, 20)
    
    # P3 Variants (Wedding Kurta)
    v_p3_mrn_l = create_variant(p3, "Maroon", "L")
    v_p3_bge_m = create_variant(p3, "Beige", "M")
    db.add_all([v_p3_mrn_l, v_p3_bge_m])
    await db.flush()
    add_inv(v_p3_mrn_l, b1, 5); add_inv(v_p3_mrn_l, b2, 2); add_inv(v_p3_mrn_l, b3, 3)
    add_inv(v_p3_bge_m, b1, 0); add_inv(v_p3_bge_m, b2, 0); add_inv(v_p3_bge_m, b3, 0) # completely OOS

    # P4 Variants (Basic T-Shirt)
    v_p4_blk_m = create_variant(p4, "Black", "M")
    db.add_all([v_p4_blk_m])
    await db.flush()
    add_inv(v_p4_blk_m, b1, 100); add_inv(v_p4_blk_m, b2, 100); add_inv(v_p4_blk_m, b3, 100)
    
    # P5 Variants (Chinos)
    v_p5_nvy_32 = create_variant(p5, "Navy", "32")
    v_p5_olv_34 = create_variant(p5, "Olive", "34")
    db.add_all([v_p5_nvy_32, v_p5_olv_34])
    await db.flush()
    add_inv(v_p5_nvy_32, b1, 30); add_inv(v_p5_nvy_32, b2, 10); add_inv(v_p5_nvy_32, b3, 20)
    add_inv(v_p5_olv_34, b1, 15); add_inv(v_p5_olv_34, b2, 10); add_inv(v_p5_olv_34, b3, 5)

    # P6 Variants (Bomber Jacket)
    v_p6_blk_l = create_variant(p6, "Black", "L")
    db.add_all([v_p6_blk_l])
    await db.flush()
    add_inv(v_p6_blk_l, b1, 10); add_inv(v_p6_blk_l, b2, 10); add_inv(v_p6_blk_l, b3, 10)

    # 7. Promotions
    off1 = Offer(offer_code="WELCOME10", offer_name="Welcome 10% Off", description="10% off store-wide", discount_percentage=Decimal("10.00"), benefit_type="PERCENTAGE", target_scope="STORE_WIDE", valid_from=now, is_active=True, priority=1)
    
    # Case H: Offer with min cart value
    off2 = Offer(offer_code="SAVE2000", offer_name="Flat Rs 2000 Off", description="Rs 2000 off on orders above Rs 10000", discount_amount=Decimal("2000.00"), benefit_type="FIXED", target_scope="STORE_WIDE", min_cart_value=Decimal("10000.00"), valid_from=now, is_active=True, priority=2)
    
    # Category target offer
    off3 = Offer(offer_code="WINTERJACKETS", offer_name="25% Off Jackets", description="Winter Sale on Jackets", discount_percentage=Decimal("25.00"), benefit_type="PERCENTAGE", target_scope="CATEGORY", target_category_id=c_outer.category_id, valid_from=now, is_active=True, priority=3)

    db.add_all([off1, off2, off3])
    
    await db.commit()
    print("Database seeded successfully with extensive Northstar Menswear data!")

async def main():
    async for db in get_db():
        await seed_db(db)
        break 

if __name__ == "__main__":
    asyncio.run(main())
