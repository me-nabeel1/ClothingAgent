"""Database seeder for the Northstar Menswear demo store (Generated)."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db, Base, get_engine
from app.catalog.models import Branch, Category, Product, ProductVariant, Color, Size, ProductImage
from app.inventory.models import BranchInventory
from app.promotions.models import Offer

async def seed_db(db: AsyncSession):
    # 0. Automatically create schema and tables if they don't exist yet
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS clothing_store;"))
        await conn.run_sync(Base.metadata.create_all)

    # Set fixed seed for deterministic product generation so the demo is stable
    random.seed(42)

    tables = [
        "branches", "categories", "colors", "sizes", "offers",
        "products", "product_variants", "branch_inventory", "product_images"
    ]
    for table in tables:
        await db.execute(text(f"TRUNCATE TABLE clothing_store.{table} CASCADE"))
    
    now = datetime.now(timezone.utc)
    
    # 1. Branches
    branches = {
        "ISB-F7": Branch(branch_code="ISB-F7", branch_name="Northstar F-7", city="Islamabad", address="F-7 Markaz", is_active=True, created_at=now),
        "ISB-GG": Branch(branch_code="ISB-GG", branch_name="Northstar Gulberg Greens", city="Islamabad", address="Gulberg", is_active=True, created_at=now),
        "LHR-MR": Branch(branch_code="LHR-MR", branch_name="Northstar Mall Road", city="Lahore", address="Mall Road", is_active=True, created_at=now)
    }
    db.add_all(branches.values())
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
        "Activewear": Category(category_name="Activewear", category_code="ACTIVEWEAR", is_active=True),
        "Gym Wear": Category(category_name="Gym Wear", category_code="GYMWEAR", is_active=True),
        "Trousers": Category(category_name="Trousers", category_code="TROUSERS", is_active=True),
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

    # Generator Configuration
    cat_config = {
        "Shirts": {
            "types": ["shirt"], "occasions": ["formal", "casual", "party"],
            "materials": ["Cotton", "Linen", "Silk", "Poly-Blend"], "fits": ["Slim", "Regular", "Relaxed"],
            "names": ["Oxford Shirt", "Linen Shirt", "Dress Shirt", "Button-Down", "Printed Shirt"],
            "prefixes": ["Premium", "Classic", "Modern", "Essential", "Casual"],
            "price_range": (2000, 6000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/regent_oxford_formal_shirt_white.webp",
                "/assets/products/essential_cotton_button_down_pale_blue.webp",
                "/assets/products/harbor_linen_blend_shirt_light_blue.webp",
                "/assets/products/breeze_short_sleeve_shirt_peach.webp",
                "/assets/products/breeze_short_sleeve_shirt_sand.webp",
                "/assets/products/heritage_pique_polo_navy_blue.webp",
                "/assets/products/monarch_mandarin_collar_shirt_cream.webp",
                "/assets/products/monarch_mandarin_collar_beige.webp"
            ]
        },
        "T-Shirts": {
            "types": ["t_shirt", "polo"], "occasions": ["casual", "gym"],
            "materials": ["Cotton", "Polyester", "Pique"], "fits": ["Regular", "Slim", "Oversized"],
            "names": ["Crew Neck T-Shirt", "V-Neck T-Shirt", "Polo Shirt", "Graphic Tee"],
            "prefixes": ["Basic", "Premium", "Athletic", "Vintage", "Essential"],
            "price_range": (800, 3000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/core_crew_neck_tshirt_white.webp",
                "/assets/products/core_crew_neck_tshirt_lightgray.webp",
                "/assets/products/city_grid_graphic_tshirt_black.webp",
                "/assets/products/city_grid_graphic_tshirt_charcoal.webp",
                "/assets/products/flex_compression_tee_black.webp",
                "/assets/products/flex_compression_tee_blue.webp",
                "/assets/products/limited_drop_neon_tee_lime.webp",
                "/assets/products/limited_drop_neon_tee_neon_green.webp",
                "/assets/products/velocity_training_tshirt_black.webp",
                "/assets/products/velocity_training_tshirt_navy.webp",
                "/assets/products/velocity_training_tshirt_teal.webp"
            ]
        },
        "Pants": {
            "types": ["chino", "dress_pants"], "occasions": ["casual", "formal", "business"],
            "materials": ["Cotton Blend", "Poly-Viscose", "Linen"], "fits": ["Slim", "Straight", "Tailored"],
            "names": ["Chinos", "Dress Pants", "Khakis", "Flat Front Pants"],
            "prefixes": ["Everyday", "Formal", "Classic", "Stretch", "Premium"],
            "price_range": (2500, 6500), "size_range": ["30", "32", "34", "36", "38"],
            "images": [
                "/assets/products/classic_cotton_pants_brown.webp",
                "/assets/products/classic_cotton_pants_taupe.webp",
                "/assets/products/avenue_cotton_chinos_khaki.webp",
                "/assets/products/utility_six_pocket_cargo_olive_green.webp"
            ]
        },
        "Traditional": {
            "types": ["kurta", "shalwar_kameez", "sherwani"], "occasions": ["wedding", "eid", "casual"],
            "materials": ["Cotton", "Silk Blend", "Brocade", "Wash-n-Wear"], "fits": ["Regular", "Tailored"],
            "names": ["Kurta", "Shalwar Kameez", "Sherwani", "Waistcoat"],
            "prefixes": ["Embroidered", "Festive", "Classic", "Premium", "Designer"],
            "price_range": (3000, 25000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/monarch_mandarin_collar_beige.webp",
                "/assets/products/monarch_mandarin_collar_shirt_cream.webp"
            ]
        },
        "Outerwear": {
            "types": ["jacket", "bomber_jacket", "leather_jacket", "hoodie"], "occasions": ["casual", "party", "winter"],
            "materials": ["Polyester", "Leather", "Fleece", "Wool"], "fits": ["Regular", "Slim", "Relaxed"],
            "names": ["Bomber Jacket", "Moto Jacket", "Winter Hoodie", "Trench Coat", "Puffer Jacket"],
            "prefixes": ["Classic", "Premium", "Warm", "Stylish", "Rugged"],
            "price_range": (4000, 15000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/metro_fleece_hoodie_burgundy.webp",
                "/assets/products/metro_fleece_hoodie_maroon.webp"
            ]
        },
        "Formal Wear": {
            "types": ["suit", "blazer", "tuxedo"], "occasions": ["business", "wedding", "formal"],
            "materials": ["Wool Blend", "Poly-Viscose", "Italian Wool"], "fits": ["Tailored", "Slim", "Classic"],
            "names": ["Two-Piece Suit", "Three-Piece Suit", "Formal Blazer", "Tuxedo"],
            "prefixes": ["Executive", "Premium", "Designer", "Classic", "Sharp"],
            "price_range": (8000, 25000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/regent_oxford_formal_shirt_white.webp",
                "/assets/products/executive_pleated_trousers_black.webp"
            ]
        },
        "Jeans": {
            "types": ["jeans"], "occasions": ["casual", "party"],
            "materials": ["Denim", "Stretch Denim"], "fits": ["Skinny", "Slim", "Straight", "Bootcut"],
            "names": ["Blue Denim", "Black Jeans", "Faded Jeans", "Ripped Jeans"],
            "prefixes": ["Classic", "Stretch", "Rugged", "Premium", "Everyday"],
            "price_range": (2000, 6000), "size_range": ["30", "32", "34", "36", "38"],
            "images": [
                "/assets/products/ridge_slim_fit_jeans_medium_blue.webp",
                "/assets/products/foundry_straight_jeans_dark_blue.webp",
                "/assets/products/weekend_denim_shorts_medium_blue.webp"
            ]
        },
        "Activewear": {
            "types": ["shorts", "joggers", "tracksuit"], "occasions": ["gym", "casual", "running"],
            "materials": ["Polyester Blend", "Fleece", "Spandex"], "fits": ["Regular", "Slim", "Athletic"],
            "names": ["Running Shorts", "Fleece Joggers", "Track Pants", "Tracksuit"],
            "prefixes": ["Performance", "Breathable", "Lightweight", "Pro", "Core"],
            "price_range": (1500, 5000), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/aero_gym_joggers_dark_gray.webp",
                "/assets/products/motion_training_shorts_black.webp",
                "/assets/products/motion_training_shorts_charcoal.webp",
                "/assets/products/motion_training_shorts_teal.webp",
                "/assets/products/sprint_tapered_track_pants_black.webp",
                "/assets/products/sprint_tapered_track_pants_charcoal.webp",
                "/assets/products/sprint_tapered_track_pants_teal.webp"
            ]
        },
        "Gym Wear": {
            "types": ["t_shirt", "tank_top", "compression"], "occasions": ["gym", "workout", "running"],
            "materials": ["Spandex", "Mesh", "Moisture-wicking Polyester"], "fits": ["Tight", "Athletic", "Regular"],
            "names": ["Compression T-Shirt", "Tank Top", "Workout Tee", "Muscle Shirt"],
            "prefixes": ["Pro", "Elite", "Breathable", "Core", "Performance"],
            "price_range": (1000, 3500), "size_range": ["S", "M", "L", "XL", "XXL"],
            "images": [
                "/assets/products/flex_compression_tee_black.webp",
                "/assets/products/flex_compression_tee_blue.webp",
                "/assets/products/velocity_training_tshirt_black.webp",
                "/assets/products/velocity_training_tshirt_navy.webp",
                "/assets/products/velocity_training_tshirt_teal.webp"
            ]
        },
        "Trousers": {
            "types": ["trousers", "cargo"], "occasions": ["casual", "business", "outdoor"],
            "materials": ["Cotton", "Twill", "Linen Blend"], "fits": ["Relaxed", "Straight", "Slim"],
            "names": ["Cotton Trousers", "Cargo Pants", "Pleated Trousers"],
            "prefixes": ["Casual", "Classic", "Utility", "Premium", "Everyday"],
            "price_range": (2000, 5500), "size_range": ["30", "32", "34", "36", "38"],
            "images": [
                "/assets/products/comfort_stretch_trousers_charcoal_gray.webp",
                "/assets/products/executive_pleated_trousers_black.webp",
                "/assets/products/studio_drawstring_trousers_stone.webp",
                "/assets/products/studio_drawstring_trousers_taupe.webp"
            ]
        }
    }

    all_products = []
    product_variants = []
    
    product_counter = 1
    
    for cat_name, conf in cat_config.items():
        cat_id = cats[cat_name].category_id
        
        # Generate 12 products for each category
        for i in range(12):
            p_type = random.choice(conf["types"])
            occ = random.choice(conf["occasions"])
            mat = random.choice(conf["materials"])
            fit = random.choice(conf["fits"])
            sea = random.choice(["Summer", "Winter", "All Season"])
            
            p_name = f"{random.choice(conf['prefixes'])} {random.choice(conf['names'])}"
            price = random.randint(conf["price_range"][0], conf["price_range"][1]) // 100 * 100
            cost_price = price * 0.4
            
            art_code = f"NS-{cat_name[:2].upper()}-{str(product_counter).zfill(4)}"
            
            p = Product(
                article_code=art_code, product_name=p_name, category_id=cat_id,
                product_type=p_type, occasion=occ, gender="MEN", brand="Northstar",
                material=mat, fit=fit, season=sea, base_cost_price=Decimal(str(cost_price)),
                base_selling_price=Decimal(str(price)), availability_scope="STORE_WIDE", product_status="ACTIVE"
            )
            db.add(p)
            all_products.append(p)
            product_counter += 1

    await db.flush()
    
    for p in all_products:
        cat_name = [k for k, v in cats.items() if v.category_id == p.category_id][0]
        conf = cat_config[cat_name]
        
        # Add primary image
        img_url = random.choice(conf["images"])
        db.add(ProductImage(
            product_id=p.product_id, color_id=None, image_path=img_url,
            alt_text=p.product_name, display_order=1, is_primary=True
        ))

        # Generate 2-4 colors per product
        selected_colors = random.sample(list(colors.values()), random.randint(2, 4))
        
        for color in selected_colors:
            # Generate 3-5 sizes per color
            selected_sizes = random.sample(conf["size_range"], random.randint(3, len(conf["size_range"])))
            for sz_label in selected_sizes:
                sz = sizes[sz_label]
                col_code = color.color_code
                v = ProductVariant(
                    product_id=p.product_id, color_id=color.color_id, size_id=sz.size_id,
                    sku=f"{p.article_code}-{col_code}-{sz_label}", 
                    barcode=f"{p.article_code.replace('-','')}{col_code}{sz_label}",
                    cost_price=p.base_cost_price, selling_price=p.base_selling_price, is_active=True
                )
                db.add(v)
                product_variants.append(v)
    
    await db.flush()

    # Add Inventory
    all_branches = list(branches.values())
    
    for v in product_variants:
        for b in all_branches:
            # 10% chance to be out of stock
            qty = 0 if random.random() < 0.1 else random.randint(5, 50)
            db.add(BranchInventory(
                variant_id=v.variant_id, branch_id=b.branch_id, quantity_on_hand=qty,
                reserved_quantity=0, damaged_quantity=0, in_transit_quantity=0, reorder_level=5, updated_at=now
            ))
            
    # 7. Promotions
    off1 = Offer(offer_code="WELCOME10", offer_name="Welcome 10% Off", description="10% off store-wide", discount_percentage=Decimal("10.00"), benefit_type="PERCENTAGE", target_scope="STORE_WIDE", valid_from=now, is_active=True, priority=1)
    off2 = Offer(offer_code="SAVE2000", offer_name="Flat Rs 2000 Off", description="Rs 2000 off on orders above Rs 10000", discount_amount=Decimal("2000.00"), benefit_type="FIXED", target_scope="STORE_WIDE", min_cart_value=Decimal("10000.00"), valid_from=now, is_active=True, priority=2)
    off3 = Offer(offer_code="WINTERJACKETS", offer_name="25% Off Jackets", description="Winter Sale on Jackets", discount_percentage=Decimal("25.00"), benefit_type="PERCENTAGE", target_scope="CATEGORY", target_category_id=cats["Outerwear"].category_id, valid_from=now, is_active=True, priority=3)

    db.add_all([off1, off2, off3])
    
    await db.commit()
    print(f"Database seeded successfully with {len(all_products)} products and {len(product_variants)} variants!")

async def main():
    async for db in get_db():
        await seed_db(db)
        break 

if __name__ == "__main__":
    asyncio.run(main())
