-- Seed 25 additional mock products across various categories with variants and inventory

BEGIN;

-- 1. Formal Shirts (Category 2)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0025', 'Oxford Classic White Shirt', 2, 'MEN', 'EliteWear', 1500, 3990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-0025-WHT-M', 1500, 3990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 50 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0026', 'Executive Pinpoint Shirt', 2, 'MEN', 'EliteWear', 1600, 4190) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-0026-SKY-L', 1600, 4190 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 35 FROM v;

-- 2. Casual / Cotton Shirts (Category 3)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0027', 'Summer Linen Casual Shirt', 3, 'MEN', 'CasualVibe', 1200, 2990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-0027-NAV-M', 1200, 2990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 40 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0028', 'Printed Vacation Shirt', 3, 'MEN', 'CasualVibe', 1100, 2790) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-0028-BLK-L', 1100, 2790 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 60 FROM v;

-- 3. T-Shirts (Category 4)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0029', 'V-Neck Essential Tee', 4, 'UNISEX', 'BasicThread', 600, 1590) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-0029-BLK-S', 600, 1590 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 100 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0030', 'Oversized Streetwear Tee', 4, 'UNISEX', 'UrbanEdge', 800, 1990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-0030-OLV-XL', 800, 1990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 80 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0031', 'Graphic Print Tee', 4, 'UNISEX', 'UrbanEdge', 900, 2190) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-0031-WHT-M', 900, 2190 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 90 FROM v;

-- 4. Polos (Category 5)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0032', 'Classic Cotton Polo', 5, 'MEN', 'PoloClub', 1200, 2990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-0032-NAV-M', 1200, 2990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 50 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0033', 'Performance Golf Polo', 5, 'MEN', 'ActiveFit', 1400, 3290) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-0033-WHT-L', 1400, 3290 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 45 FROM v;

-- 5. Jeans (Category 7)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0034', 'Skinny Fit Black Jeans', 7, 'MEN', 'DenimPro', 2000, 4890) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-0034-BLK-32', 2000, 4890 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 40 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0035', 'Relaxed Fit Blue Jeans', 7, 'MEN', 'DenimPro', 2100, 4990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-0035-NAV-34', 2100, 4990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 30 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0036', 'Ripped Edge Jeans', 7, 'MEN', 'UrbanEdge', 2300, 5290) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-0036-SKY-32', 2300, 5290 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 25 FROM v;

-- 6. Cotton Pants / Chinos (Category 8)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0037', 'Khaki Smart Chinos', 8, 'MEN', 'SmartCasual', 1600, 3990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-0037-OLV-32', 1600, 3990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 60 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0038', 'Navy Everyday Chinos', 8, 'MEN', 'SmartCasual', 1600, 3990) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-0038-NAV-34', 1600, 3990 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 55 FROM v;

-- 7. Trousers (Category 9)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0039', 'Slim Fit Checkered Trousers', 9, 'MEN', 'EliteWear', 1800, 4590) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-0039-BLK-32', 1800, 4590 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 35 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0040', 'Classic Tailored Trousers', 9, 'MEN', 'EliteWear', 1900, 4690) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-0040-NAV-34', 1900, 4690 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 40 FROM v;

-- 8. Shorts (Category 10)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0041', 'Bermuda Cotton Shorts', 10, 'MEN', 'SummerWear', 1000, 2490) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-0041-SKY-M', 1000, 2490 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 80 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0042', 'Athletic Running Shorts', 10, 'UNISEX', 'ActiveFit', 900, 2290) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-0042-BLK-S', 900, 2290 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 90 FROM v;

-- 9. Cargo Pants (Category 11)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0043', 'Olive Tactical Cargos', 11, 'MEN', 'UtilityGear', 1800, 4490) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-0043-OLV-L', 1800, 4490 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 45 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0044', 'Black Street Cargos', 11, 'MEN', 'UrbanEdge', 1900, 4690) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-0044-BLK-M', 1900, 4690 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 50 FROM v;

-- 10. Gym Wear (Category 13)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0045', 'DryFit Muscle Tank', 13, 'MEN', 'ActiveFit', 700, 1890) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-0045-BLK-M', 700, 1890 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 65 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0046', 'Seamless Gym Tee', 13, 'UNISEX', 'ActiveFit', 800, 2190) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-0046-WHT-L', 800, 2190 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 70 FROM v;

-- 11. Track Pants (Category 14)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0047', 'Pro Training Track Pants', 14, 'UNISEX', 'ActiveFit', 1400, 3490) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-0047-NAV-M', 1400, 3490 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 55 FROM v;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0048', 'Fleece Lined Joggers', 14, 'UNISEX', 'ComfortWear', 1500, 3690) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-0048-BLK-L', 1500, 3690 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 60 FROM v;

-- 12. Hoodies (Category 15)
WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-0049', 'Essential Zip-Up Hoodie', 15, 'UNISEX', 'ComfortWear', 2000, 4890) RETURNING product_id),
v AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-0049-BLK-M', 2000, 4890 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand) SELECT 1, variant_id, 40 FROM v;

COMMIT;
