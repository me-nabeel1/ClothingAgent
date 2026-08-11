"""Database seeder for the Northstar Menswear demo store."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.catalog.models import Branch, Category, Product, ProductVariant, Color, Size, ProductImage
from app.inventory.models import BranchInventory
from app.promotions.models import Offer

async def seed_db(db: AsyncSession):
    # Truncate all relevant tables
    tables = [
        "branches", "categories", "colors", "sizes", "offers",
        "products", "product_variants", "branch_inventory", "product_images"
    ]
    for table in tables:
        await db.execute(text(f"TRUNCATE TABLE clothing_store.{table} CASCADE"))
    
    now = datetime.now(timezone.utc)
    
    # 1. Branches
    b1 = Branch(branch_code="ISB-F7", branch_name="Northstar F-7", city="Islamabad", address="F-7 Markaz", is_active=True, created_at=now)
    b2 = Branch(branch_code="ISB-GG", branch_name="Northstar Gulberg Greens", city="Islamabad", address="Gulberg", is_active=True, created_at=now)
    b3 = Branch(branch_code="LHR-MR", branch_name="Northstar Mall Road", city="Lahore", address="Mall Road", is_active=True, created_at=now)
    db.add_all([b1, b2, b3])
    await db.flush()

    # 2. Categories
    cats = {
        "Shirts": Category(category_name="Shirts", category_code="SHIRTS", is_active=True),
        "T-Shirts": Category(category_name="T-Shirts", category_code="TSHIRTS", is_active=True),
        "Pants": Category(category_name="Pants", category_code="PANTS", is_active=True),
        "Traditional": Category(category_name="Traditional", category_code="TRADITIONAL", is_active=True),
        "Outerwear": Category(category_name="Outerwear", category_code="OUTERWEAR", is_active=True),
        "Formal Wear": Category(category_name="Formal Wear", category_code="FORMAL", is_active=True),
        "Jeans": Category(category_name="Jeans", category_code="JEANS", is_active=True),
    }
    db.add_all(cats.values())
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
        "Red": Color(color_name="Red", color_code="RED", hex_code="#FF0000"),
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
    def create_product(art, name, cat, ptype, occ, mat, fit, sea, cp, sp):
        return Product(
            article_code=art, product_name=name, category_id=cats[cat].category_id,
            product_type=ptype, occasion=occ, gender="MEN", brand="Northstar",
            material=mat, fit=fit, season=sea, base_cost_price=Decimal(str(cp)),
            base_selling_price=Decimal(str(sp)), availability_scope="STORE_WIDE", product_status="ACTIVE"
        )
    
    p1 = create_product("NS-SH-001", "Premium Oxford Shirt", "Shirts", "shirt", "formal", "Cotton", "Slim", "All Season", 1500, 4500)
    p2 = create_product("NS-SH-002", "Casual Linen Shirt", "Shirts", "shirt", "casual", "Linen", "Relaxed", "Summer", 1200, 3500)
    p3 = create_product("NS-TR-001", "Embroidered Wedding Kurta", "Traditional", "kurta", "wedding", "Silk Blend", "Regular", "All Season", 4000, 9500)
    p4 = create_product("NS-TS-001", "Basic Crew Neck T-Shirt", "T-Shirts", "t_shirt", "casual", "Cotton", "Regular", "Summer", 500, 1500)
    p5 = create_product("NS-PA-001", "Everyday Chinos", "Pants", "chino", "casual", "Cotton Blend", "Slim", "All Season", 1800, 4500)
    p6 = create_product("NS-JA-001", "Classic Bomber Jacket", "Outerwear", "bomber_jacket", "casual", "Polyester", "Regular", "Winter", 4500, 11000)
    p7 = create_product("NS-FW-001", "Executive Two-Piece Suit", "Formal Wear", "suit", "business", "Wool Blend", "Tailored", "Winter", 8000, 18000)
    p8 = create_product("NS-JE-001", "Classic Blue Denim", "Jeans", "jeans", "casual", "Denim", "Straight", "All Season", 2000, 5000)
    p9 = create_product("NS-HO-001", "Fleece Winter Hoodie", "Outerwear", "hoodie", "casual", "Fleece", "Relaxed", "Winter", 2500, 6000)
    p10 = create_product("NS-TR-002", "Festive Shalwar Kameez", "Traditional", "shalwar_kameez", "eid", "Cotton", "Regular", "Summer", 3000, 7000)
    p11 = create_product("NS-SH-003", "Party Wear Silk Shirt", "Shirts", "shirt", "party", "Silk", "Slim", "All Season", 2500, 6500)
    p12 = create_product("NS-PA-002", "Formal Dress Pants", "Pants", "dress_pants", "formal", "Poly-Viscose", "Tailored", "All Season", 2200, 5500)
    p13 = create_product("NS-TS-002", "Polo T-Shirt", "T-Shirts", "polo", "casual", "Pique Cotton", "Regular", "Summer", 800, 2200)
    p14 = create_product("NS-JA-002", "Leather Moto Jacket", "Outerwear", "leather_jacket", "party", "Leather", "Slim", "Winter", 12000, 25000)
    p15 = create_product("NS-TR-003", "Sherwani", "Traditional", "sherwani", "wedding", "Brocade", "Tailored", "Winter", 15000, 35000)

    all_products = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15]
    db.add_all(all_products)
    await db.flush()

    # Images
    def add_img(prod, url, is_prim=True, order=1, color=None):
        db.add(ProductImage(
            product_id=prod.product_id,
            color_id=colors[color].color_id if color else None,
            image_path=url,
            alt_text=prod.product_name,
            display_order=order,
            is_primary=is_prim
        ))

    add_img(p1, "https://images.unsplash.com/photo-1596755094514-f87e32f85e2c?w=500&q=80")
    add_img(p2, "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=500&q=80")
    add_img(p3, "https://images.unsplash.com/photo-1597983073493-88cd35f47448?w=500&q=80")
    add_img(p4, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&q=80")
    add_img(p5, "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&q=80")
    add_img(p6, "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500&q=80")
    add_img(p7, "https://images.unsplash.com/photo-1594938298596-70f56fb3cecb?w=500&q=80")
    add_img(p8, "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&q=80")
    add_img(p9, "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500&q=80")
    add_img(p10, "https://images.unsplash.com/photo-1597983073493-88cd35f47448?w=500&q=80") # reusing traditional
    add_img(p11, "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&q=80")
    add_img(p12, "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&q=80")
    add_img(p13, "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&q=80")
    add_img(p14, "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&q=80")
    add_img(p15, "https://images.unsplash.com/photo-1597983073493-88cd35f47448?w=500&q=80")

    # 6. Variants and Inventory
    def create_variant(prod, col, sz, is_active=True):
        return ProductVariant(
            product_id=prod.product_id, color_id=colors[col].color_id, size_id=sizes[sz].size_id,
            sku=f"{prod.article_code}-{col[:1].upper()}-{sz}", barcode=f"{prod.article_code.replace('-','')}{col[:1].upper()}{sz}",
            cost_price=prod.base_cost_price, selling_price=prod.base_selling_price, is_active=is_active
        )
        
    def add_inv(v, b, qty):
        db.add(BranchInventory(
            variant_id=v.variant_id, branch_id=b.branch_id, quantity_on_hand=qty,
            reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=5, updated_at=now
        ))

    # P1: Available everywhere
    v_p1_blk_m = create_variant(p1, "Black", "M")
    v_p1_wht_l = create_variant(p1, "White", "L")
    db.add_all([v_p1_blk_m, v_p1_wht_l])
    await db.flush()
    add_inv(v_p1_blk_m, b1, 10); add_inv(v_p1_blk_m, b2, 5); add_inv(v_p1_blk_m, b3, 10)
    add_inv(v_p1_wht_l, b1, 15); add_inv(v_p1_wht_l, b2, 10); add_inv(v_p1_wht_l, b3, 20)

    # P2: Branch difference & Partial OOS (WHT-L OOS in F7, NVY-M avail everywhere)
    v_p2_wht_l = create_variant(p2, "White", "L")
    v_p2_nvy_m = create_variant(p2, "Navy", "M")
    db.add_all([v_p2_wht_l, v_p2_nvy_m])
    await db.flush()
    add_inv(v_p2_wht_l, b1, 0); add_inv(v_p2_wht_l, b2, 0); add_inv(v_p2_wht_l, b3, 10)
    add_inv(v_p2_nvy_m, b1, 20); add_inv(v_p2_nvy_m, b2, 20); add_inv(v_p2_nvy_m, b3, 20)
    
    # P3: Wedding - Partial OOS
    v_p3_mrn_l = create_variant(p3, "Maroon", "L")
    v_p3_bge_m = create_variant(p3, "Beige", "M")
    db.add_all([v_p3_mrn_l, v_p3_bge_m])
    await db.flush()
    add_inv(v_p3_mrn_l, b1, 5); add_inv(v_p3_mrn_l, b2, 2); add_inv(v_p3_mrn_l, b3, 3)
    add_inv(v_p3_bge_m, b1, 0); add_inv(v_p3_bge_m, b2, 0); add_inv(v_p3_bge_m, b3, 0) # completely OOS

    # P4: Plentiful
    v_p4_blk_m = create_variant(p4, "Black", "M")
    v_p4_wht_m = create_variant(p4, "White", "M")
    db.add_all([v_p4_blk_m, v_p4_wht_m])
    await db.flush()
    add_inv(v_p4_blk_m, b1, 100); add_inv(v_p4_blk_m, b2, 100); add_inv(v_p4_blk_m, b3, 100)
    add_inv(v_p4_wht_m, b1, 100); add_inv(v_p4_wht_m, b2, 100); add_inv(v_p4_wht_m, b3, 100)
    
    # P5: Chinos
    v_p5_nvy_32 = create_variant(p5, "Navy", "32")
    v_p5_olv_34 = create_variant(p5, "Olive", "34")
    db.add_all([v_p5_nvy_32, v_p5_olv_34])
    await db.flush()
    add_inv(v_p5_nvy_32, b1, 30); add_inv(v_p5_nvy_32, b2, 10); add_inv(v_p5_nvy_32, b3, 20)
    add_inv(v_p5_olv_34, b1, 15); add_inv(v_p5_olv_34, b2, 10); add_inv(v_p5_olv_34, b3, 5)

    # P6: Jackets
    v_p6_blk_l = create_variant(p6, "Black", "L")
    v_p6_nvy_l = create_variant(p6, "Navy", "L")
    db.add_all([v_p6_blk_l, v_p6_nvy_l])
    await db.flush()
    add_inv(v_p6_blk_l, b1, 10); add_inv(v_p6_blk_l, b2, 10); add_inv(v_p6_blk_l, b3, 10)
    add_inv(v_p6_nvy_l, b1, 0); add_inv(v_p6_nvy_l, b2, 0); add_inv(v_p6_nvy_l, b3, 0) # completely OOS

    # P7: Suit
    v_p7_blk_40 = create_variant(p7, "Black", "M") # Using M for 40
    v_p7_nvy_42 = create_variant(p7, "Navy", "L")
    db.add_all([v_p7_blk_40, v_p7_nvy_42])
    await db.flush()
    add_inv(v_p7_blk_40, b1, 2); add_inv(v_p7_blk_40, b2, 1); add_inv(v_p7_blk_40, b3, 1)
    add_inv(v_p7_nvy_42, b1, 0); add_inv(v_p7_nvy_42, b2, 0); add_inv(v_p7_nvy_42, b3, 5) # Only in LHR

    # P8: Jeans
    v_p8_blu_32 = create_variant(p8, "Blue", "32")
    db.add_all([v_p8_blu_32])
    await db.flush()
    add_inv(v_p8_blu_32, b1, 50); add_inv(v_p8_blu_32, b2, 50); add_inv(v_p8_blu_32, b3, 50)

    # P9: Hoodie
    v_p9_gry_l = create_variant(p9, "Grey", "L")
    db.add_all([v_p9_gry_l])
    await db.flush()
    add_inv(v_p9_gry_l, b1, 20); add_inv(v_p9_gry_l, b2, 20); add_inv(v_p9_gry_l, b3, 20)

    # P10: Eid
    v_p10_wht_l = create_variant(p10, "White", "L")
    db.add_all([v_p10_wht_l])
    await db.flush()
    add_inv(v_p10_wht_l, b1, 30); add_inv(v_p10_wht_l, b2, 30); add_inv(v_p10_wht_l, b3, 30)
    
    # P11: Party
    v_p11_blk_s = create_variant(p11, "Black", "S")
    db.add_all([v_p11_blk_s])
    await db.flush()
    add_inv(v_p11_blk_s, b1, 5); add_inv(v_p11_blk_s, b2, 0); add_inv(v_p11_blk_s, b3, 0)
    
    # P12: Formal Pants
    v_p12_gry_34 = create_variant(p12, "Grey", "34")
    db.add_all([v_p12_gry_34])
    await db.flush()
    add_inv(v_p12_gry_34, b1, 0); add_inv(v_p12_gry_34, b2, 0); add_inv(v_p12_gry_34, b3, 0) # completely OOS

    # P13: Polo
    v_p13_blu_m = create_variant(p13, "Blue", "M")
    db.add_all([v_p13_blu_m])
    await db.flush()
    add_inv(v_p13_blu_m, b1, 25); add_inv(v_p13_blu_m, b2, 25); add_inv(v_p13_blu_m, b3, 25)
    
    # P14: Leather Moto Jacket (Completely Out of stock everywhere)
    v_p14_brn_l = create_variant(p14, "Brown", "L")
    db.add_all([v_p14_brn_l])
    await db.flush()
    add_inv(v_p14_brn_l, b1, 0); add_inv(v_p14_brn_l, b2, 0); add_inv(v_p14_brn_l, b3, 0)
    
    # P15: Sherwani
    v_p15_mrn_m = create_variant(p15, "Maroon", "M")
    db.add_all([v_p15_mrn_m])
    await db.flush()
    add_inv(v_p15_mrn_m, b1, 2); add_inv(v_p15_mrn_m, b2, 0); add_inv(v_p15_mrn_m, b3, 2)

    # 7. Promotions
    off1 = Offer(offer_code="WELCOME10", offer_name="Welcome 10% Off", description="10% off store-wide", discount_percentage=Decimal("10.00"), benefit_type="PERCENTAGE", target_scope="STORE_WIDE", valid_from=now, is_active=True, priority=1)
    
    # Case H: Offer with min cart value
    off2 = Offer(offer_code="SAVE2000", offer_name="Flat Rs 2000 Off", description="Rs 2000 off on orders above Rs 10000", discount_amount=Decimal("2000.00"), benefit_type="FIXED", target_scope="STORE_WIDE", min_cart_value=Decimal("10000.00"), valid_from=now, is_active=True, priority=2)
    
    # Category target offer
    off3 = Offer(offer_code="WINTERJACKETS", offer_name="25% Off Jackets", description="Winter Sale on Jackets", discount_percentage=Decimal("25.00"), benefit_type="PERCENTAGE", target_scope="CATEGORY", target_category_id=cats["Outerwear"].category_id, valid_from=now, is_active=True, priority=3)

    db.add_all([off1, off2, off3])
    
    await db.commit()
    print("Database seeded successfully with extensive Northstar Menswear data!")

async def main():
    async for db in get_db():
        await seed_db(db)
        break 

if __name__ == "__main__":
    asyncio.run(main())
