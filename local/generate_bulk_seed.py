import random
import uuid

categories = {
    2: ("Formal Shirts", "MEN", 15, 2000, 5000),
    3: ("Casual Shirts", "MEN", 15, 1500, 3500),
    4: ("T-Shirts", "UNISEX", 20, 800, 2500),
    5: ("Polo Shirts", "MEN", 15, 1200, 3000),
    7: ("Jeans", "MEN", 11, 2500, 6000),
    8: ("Cotton Pants", "MEN", 12, 2000, 4500),
    9: ("Trousers", "MEN", 12, 2500, 5500),
    10: ("Shorts", "MEN", 12, 1000, 2500),
    11: ("Cargo Pants", "MEN", 10, 1800, 4000),
    13: ("Gym Wear", "UNISEX", 10, 1000, 3000),
    14: ("Track Pants", "UNISEX", 10, 1500, 3500),
    15: ("Hoodies", "UNISEX", 10, 2500, 6000),
}

colors = [
    (1, "BLK"),
    (2, "WHT"),
    (3, "NAV"),
    (4, "SKY"),
    (5, "OLV"),
]

sizes = [
    (1, "XS"),
    (2, "S"),
    (3, "M"),
    (4, "L"),
    (5, "XL"),
]

adjectives = ["Classic", "Modern", "Urban", "Vintage", "Essential", "Premium", "Signature", "Elevated", "Core", "Dynamic", "Performance", "Studio", "Everyday", "Signature"]
brands = ["EliteWear", "CasualVibe", "UrbanEdge", "ComfortWear", "ActiveFit", "DenimPro", "SmartCasual"]

sql_lines = ["BEGIN;"]
article_counter = 1000

for cat_id, (cat_name, gender, count, min_price, max_price) in categories.items():
    for _ in range(count):
        article_code = f"ART-{article_counter}"
        article_counter += 1
        
        adj = random.choice(adjectives)
        name = f"{adj} {cat_name}"
        brand = random.choice(brands)
        cost = random.randint(min_price, max_price)
        sell = int(cost * random.uniform(1.5, 2.5))
        
        # Product CTE
        sql = f"WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('{article_code}', '{name}', {cat_id}, '{gender}', '{brand}', {cost}, {sell}) RETURNING product_id),\n"
        
        num_variants = random.randint(2, 4)
        variants = []
        for __ in range(num_variants):
            c_id, c_code = random.choice(colors)
            s_id, s_code = random.choice(sizes)
            sku = f"{article_code}-{c_code}-{s_code}"
            
            # Avoid duplicate variants
            while any(v[0] == sku for v in variants):
                c_id, c_code = random.choice(colors)
                s_id, s_code = random.choice(sizes)
                sku = f"{article_code}-{c_code}-{s_code}"
                
            variants.append((sku, c_id, s_id))
            
        # Variant CTEs
        variant_ctes = []
        for idx, (sku, c_id, s_id) in enumerate(variants):
            v_name = f"v{idx}"
            cte = f"{v_name} AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, {c_id}, {s_id}, '{sku}', {cost}, {sell} FROM p RETURNING variant_id)"
            variant_ctes.append(cte)
            
        sql += ",\n".join(variant_ctes)
        sql += "\nINSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)\n"
        
        # Inventory Inserts
        inv_lines = []
        for idx in range(len(variants)):
            v_name = f"v{idx}"
            stock = random.randint(10, 100)
            inv = f"SELECT 1, variant_id, {stock} FROM {v_name}"
            inv_lines.append(inv)
            
        sql += "\nUNION ALL\n".join(inv_lines) + ";"
        sql_lines.append(sql)

sql_lines.append("COMMIT;")

with open("local/bulk_seed.sql", "w", encoding="utf-8") as f:
    f.write("\n\n".join(sql_lines))
