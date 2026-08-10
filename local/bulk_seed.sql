BEGIN;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1000', 'Elevated Formal Shirts', 2, 'MEN', 'ActiveFit', 2743, 6258) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1000-NAV-S', 2743, 6258 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1000-OLV-M', 2743, 6258 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1000-OLV-XL', 2743, 6258 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1000-BLK-XS', 2743, 6258 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 73 FROM v0
UNION ALL
SELECT 1, variant_id, 25 FROM v1
UNION ALL
SELECT 1, variant_id, 62 FROM v2
UNION ALL
SELECT 1, variant_id, 93 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1001', 'Modern Formal Shirts', 2, 'MEN', 'SmartCasual', 4326, 6499) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1001-NAV-XL', 4326, 6499 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1001-WHT-M', 4326, 6499 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1001-OLV-XL', 4326, 6499 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 83 FROM v0
UNION ALL
SELECT 1, variant_id, 32 FROM v1
UNION ALL
SELECT 1, variant_id, 55 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1002', 'Core Formal Shirts', 2, 'MEN', 'DenimPro', 3779, 6177) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1002-NAV-S', 3779, 6177 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1002-NAV-XL', 3779, 6177 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 45 FROM v0
UNION ALL
SELECT 1, variant_id, 34 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1003', 'Vintage Formal Shirts', 2, 'MEN', 'UrbanEdge', 2828, 5344) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1003-OLV-S', 2828, 5344 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1003-BLK-XS', 2828, 5344 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 79 FROM v0
UNION ALL
SELECT 1, variant_id, 30 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1004', 'Core Formal Shirts', 2, 'MEN', 'DenimPro', 4511, 10745) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1004-WHT-S', 4511, 10745 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1004-BLK-L', 4511, 10745 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1004-NAV-M', 4511, 10745 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1004-BLK-S', 4511, 10745 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 87 FROM v0
UNION ALL
SELECT 1, variant_id, 30 FROM v1
UNION ALL
SELECT 1, variant_id, 69 FROM v2
UNION ALL
SELECT 1, variant_id, 91 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1005', 'Performance Formal Shirts', 2, 'MEN', 'DenimPro', 3279, 6625) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1005-SKY-L', 3279, 6625 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1005-WHT-XL', 3279, 6625 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1005-NAV-S', 3279, 6625 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1005-BLK-L', 3279, 6625 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 51 FROM v0
UNION ALL
SELECT 1, variant_id, 62 FROM v1
UNION ALL
SELECT 1, variant_id, 100 FROM v2
UNION ALL
SELECT 1, variant_id, 41 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1006', 'Modern Formal Shirts', 2, 'MEN', 'CasualVibe', 3835, 9147) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1006-NAV-S', 3835, 9147 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1006-OLV-XL', 3835, 9147 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 37 FROM v0
UNION ALL
SELECT 1, variant_id, 44 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1007', 'Vintage Formal Shirts', 2, 'MEN', 'SmartCasual', 3801, 8896) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1007-OLV-XL', 3801, 8896 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1007-NAV-XS', 3801, 8896 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1007-WHT-M', 3801, 8896 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1007-SKY-XS', 3801, 8896 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 15 FROM v0
UNION ALL
SELECT 1, variant_id, 96 FROM v1
UNION ALL
SELECT 1, variant_id, 32 FROM v2
UNION ALL
SELECT 1, variant_id, 50 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1008', 'Classic Formal Shirts', 2, 'MEN', 'ActiveFit', 4559, 8330) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1008-NAV-XL', 4559, 8330 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1008-SKY-M', 4559, 8330 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1008-NAV-XS', 4559, 8330 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 77 FROM v0
UNION ALL
SELECT 1, variant_id, 77 FROM v1
UNION ALL
SELECT 1, variant_id, 95 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1009', 'Core Formal Shirts', 2, 'MEN', 'DenimPro', 3689, 7034) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1009-NAV-S', 3689, 7034 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1009-BLK-XL', 3689, 7034 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1009-NAV-XL', 3689, 7034 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 87 FROM v0
UNION ALL
SELECT 1, variant_id, 25 FROM v1
UNION ALL
SELECT 1, variant_id, 12 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1010', 'Performance Formal Shirts', 2, 'MEN', 'ActiveFit', 4717, 8318) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1010-WHT-XS', 4717, 8318 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1010-OLV-L', 4717, 8318 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1010-NAV-XS', 4717, 8318 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1010-BLK-M', 4717, 8318 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 85 FROM v0
UNION ALL
SELECT 1, variant_id, 13 FROM v1
UNION ALL
SELECT 1, variant_id, 23 FROM v2
UNION ALL
SELECT 1, variant_id, 35 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1011', 'Core Formal Shirts', 2, 'MEN', 'ActiveFit', 3992, 8625) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1011-OLV-XL', 3992, 8625 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1011-WHT-L', 3992, 8625 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1011-BLK-XL', 3992, 8625 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 61 FROM v0
UNION ALL
SELECT 1, variant_id, 88 FROM v1
UNION ALL
SELECT 1, variant_id, 38 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1012', 'Modern Formal Shirts', 2, 'MEN', 'EliteWear', 2350, 5751) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1012-SKY-S', 2350, 5751 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1012-NAV-M', 2350, 5751 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1012-OLV-M', 2350, 5751 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 76 FROM v0
UNION ALL
SELECT 1, variant_id, 65 FROM v1
UNION ALL
SELECT 1, variant_id, 30 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1013', 'Performance Formal Shirts', 2, 'MEN', 'SmartCasual', 2194, 3425) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1013-NAV-XS', 2194, 3425 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1013-WHT-XL', 2194, 3425 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1013-OLV-L', 2194, 3425 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1013-SKY-XL', 2194, 3425 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 97 FROM v0
UNION ALL
SELECT 1, variant_id, 100 FROM v1
UNION ALL
SELECT 1, variant_id, 21 FROM v2
UNION ALL
SELECT 1, variant_id, 47 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1014', 'Everyday Formal Shirts', 2, 'MEN', 'ComfortWear', 2182, 5278) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1014-NAV-S', 2182, 5278 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1014-BLK-XL', 2182, 5278 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1014-SKY-M', 2182, 5278 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 23 FROM v0
UNION ALL
SELECT 1, variant_id, 38 FROM v1
UNION ALL
SELECT 1, variant_id, 27 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1015', 'Signature Casual Shirts', 3, 'MEN', 'CasualVibe', 3217, 7346) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1015-BLK-L', 3217, 7346 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1015-OLV-XL', 3217, 7346 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1015-OLV-S', 3217, 7346 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1015-NAV-L', 3217, 7346 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 95 FROM v0
UNION ALL
SELECT 1, variant_id, 75 FROM v1
UNION ALL
SELECT 1, variant_id, 55 FROM v2
UNION ALL
SELECT 1, variant_id, 84 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1016', 'Signature Casual Shirts', 3, 'MEN', 'DenimPro', 1973, 3420) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1016-OLV-XS', 1973, 3420 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1016-NAV-M', 1973, 3420 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1016-NAV-XL', 1973, 3420 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 66 FROM v0
UNION ALL
SELECT 1, variant_id, 77 FROM v1
UNION ALL
SELECT 1, variant_id, 93 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1017', 'Vintage Casual Shirts', 3, 'MEN', 'DenimPro', 2009, 3233) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1017-OLV-L', 2009, 3233 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1017-NAV-XS', 2009, 3233 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1017-OLV-M', 2009, 3233 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 46 FROM v0
UNION ALL
SELECT 1, variant_id, 64 FROM v1
UNION ALL
SELECT 1, variant_id, 80 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1018', 'Elevated Casual Shirts', 3, 'MEN', 'UrbanEdge', 2831, 6810) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1018-WHT-XL', 2831, 6810 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1018-NAV-L', 2831, 6810 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1018-OLV-XS', 2831, 6810 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 11 FROM v0
UNION ALL
SELECT 1, variant_id, 79 FROM v1
UNION ALL
SELECT 1, variant_id, 34 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1019', 'Elevated Casual Shirts', 3, 'MEN', 'CasualVibe', 2070, 4170) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1019-BLK-L', 2070, 4170 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1019-WHT-XS', 2070, 4170 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 15 FROM v0
UNION ALL
SELECT 1, variant_id, 22 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1020', 'Classic Casual Shirts', 3, 'MEN', 'ActiveFit', 3346, 7685) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1020-NAV-M', 3346, 7685 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1020-BLK-S', 3346, 7685 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1020-OLV-S', 3346, 7685 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1020-SKY-L', 3346, 7685 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 19 FROM v0
UNION ALL
SELECT 1, variant_id, 93 FROM v1
UNION ALL
SELECT 1, variant_id, 100 FROM v2
UNION ALL
SELECT 1, variant_id, 74 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1021', 'Vintage Casual Shirts', 3, 'MEN', 'ActiveFit', 2209, 4499) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1021-OLV-L', 2209, 4499 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1021-WHT-XL', 2209, 4499 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 32 FROM v0
UNION ALL
SELECT 1, variant_id, 32 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1022', 'Everyday Casual Shirts', 3, 'MEN', 'ComfortWear', 2980, 6942) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1022-OLV-S', 2980, 6942 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1022-WHT-L', 2980, 6942 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 26 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1023', 'Signature Casual Shirts', 3, 'MEN', 'CasualVibe', 3037, 7304) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1023-SKY-XS', 3037, 7304 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1023-WHT-L', 3037, 7304 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1023-WHT-S', 3037, 7304 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1023-OLV-XS', 3037, 7304 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 55 FROM v0
UNION ALL
SELECT 1, variant_id, 29 FROM v1
UNION ALL
SELECT 1, variant_id, 16 FROM v2
UNION ALL
SELECT 1, variant_id, 41 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1024', 'Dynamic Casual Shirts', 3, 'MEN', 'UrbanEdge', 2743, 6106) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1024-NAV-XS', 2743, 6106 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1024-OLV-XS', 2743, 6106 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1024-BLK-L', 2743, 6106 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 14 FROM v0
UNION ALL
SELECT 1, variant_id, 52 FROM v1
UNION ALL
SELECT 1, variant_id, 26 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1025', 'Core Casual Shirts', 3, 'MEN', 'ComfortWear', 2533, 6280) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1025-BLK-XL', 2533, 6280 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1025-BLK-S', 2533, 6280 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 45 FROM v0
UNION ALL
SELECT 1, variant_id, 21 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1026', 'Signature Casual Shirts', 3, 'MEN', 'UrbanEdge', 1935, 4665) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1026-BLK-S', 1935, 4665 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1026-NAV-M', 1935, 4665 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 44 FROM v0
UNION ALL
SELECT 1, variant_id, 48 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1027', 'Signature Casual Shirts', 3, 'MEN', 'CasualVibe', 3038, 6726) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1027-NAV-XL', 3038, 6726 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1027-BLK-L', 3038, 6726 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1027-SKY-XL', 3038, 6726 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 42 FROM v0
UNION ALL
SELECT 1, variant_id, 21 FROM v1
UNION ALL
SELECT 1, variant_id, 91 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1028', 'Essential Casual Shirts', 3, 'MEN', 'ActiveFit', 1552, 2405) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1028-NAV-L', 1552, 2405 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1028-WHT-S', 1552, 2405 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1028-NAV-M', 1552, 2405 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1028-SKY-L', 1552, 2405 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 30 FROM v0
UNION ALL
SELECT 1, variant_id, 89 FROM v1
UNION ALL
SELECT 1, variant_id, 11 FROM v2
UNION ALL
SELECT 1, variant_id, 61 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1029', 'Signature Casual Shirts', 3, 'MEN', 'CasualVibe', 2744, 6411) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1029-NAV-XS', 2744, 6411 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1029-SKY-S', 2744, 6411 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1029-WHT-XL', 2744, 6411 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 11 FROM v0
UNION ALL
SELECT 1, variant_id, 23 FROM v1
UNION ALL
SELECT 1, variant_id, 72 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1030', 'Premium T-Shirts', 4, 'UNISEX', 'EliteWear', 1664, 2956) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1030-NAV-XL', 1664, 2956 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1030-BLK-M', 1664, 2956 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1030-NAV-S', 1664, 2956 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 66 FROM v0
UNION ALL
SELECT 1, variant_id, 27 FROM v1
UNION ALL
SELECT 1, variant_id, 14 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1031', 'Signature T-Shirts', 4, 'UNISEX', 'CasualVibe', 2493, 5223) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1031-NAV-M', 2493, 5223 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1031-SKY-M', 2493, 5223 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1031-WHT-M', 2493, 5223 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1031-BLK-XS', 2493, 5223 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 77 FROM v0
UNION ALL
SELECT 1, variant_id, 29 FROM v1
UNION ALL
SELECT 1, variant_id, 51 FROM v2
UNION ALL
SELECT 1, variant_id, 37 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1032', 'Essential T-Shirts', 4, 'UNISEX', 'ActiveFit', 2359, 3850) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1032-OLV-S', 2359, 3850 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1032-NAV-XS', 2359, 3850 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1032-OLV-L', 2359, 3850 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1032-WHT-M', 2359, 3850 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 97 FROM v0
UNION ALL
SELECT 1, variant_id, 42 FROM v1
UNION ALL
SELECT 1, variant_id, 79 FROM v2
UNION ALL
SELECT 1, variant_id, 40 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1033', 'Everyday T-Shirts', 4, 'UNISEX', 'UrbanEdge', 1172, 2409) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1033-WHT-XL', 1172, 2409 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1033-SKY-L', 1172, 2409 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1033-OLV-M', 1172, 2409 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1033-BLK-M', 1172, 2409 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 47 FROM v0
UNION ALL
SELECT 1, variant_id, 86 FROM v1
UNION ALL
SELECT 1, variant_id, 75 FROM v2
UNION ALL
SELECT 1, variant_id, 63 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1034', 'Dynamic T-Shirts', 4, 'UNISEX', 'SmartCasual', 2317, 4759) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1034-SKY-S', 2317, 4759 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1034-OLV-XS', 2317, 4759 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1034-WHT-M', 2317, 4759 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 20 FROM v0
UNION ALL
SELECT 1, variant_id, 86 FROM v1
UNION ALL
SELECT 1, variant_id, 16 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1035', 'Signature T-Shirts', 4, 'UNISEX', 'CasualVibe', 1758, 2910) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1035-OLV-XL', 1758, 2910 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1035-BLK-S', 1758, 2910 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1035-OLV-XS', 1758, 2910 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 75 FROM v0
UNION ALL
SELECT 1, variant_id, 63 FROM v1
UNION ALL
SELECT 1, variant_id, 25 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1036', 'Performance T-Shirts', 4, 'UNISEX', 'ComfortWear', 2485, 5536) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1036-OLV-XS', 2485, 5536 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1036-SKY-XL', 2485, 5536 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1036-WHT-L', 2485, 5536 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1036-SKY-XS', 2485, 5536 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 10 FROM v0
UNION ALL
SELECT 1, variant_id, 37 FROM v1
UNION ALL
SELECT 1, variant_id, 81 FROM v2
UNION ALL
SELECT 1, variant_id, 87 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1037', 'Urban T-Shirts', 4, 'UNISEX', 'ActiveFit', 1529, 2775) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1037-SKY-L', 1529, 2775 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1037-WHT-L', 1529, 2775 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1037-NAV-M', 1529, 2775 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 77 FROM v0
UNION ALL
SELECT 1, variant_id, 31 FROM v1
UNION ALL
SELECT 1, variant_id, 53 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1038', 'Premium T-Shirts', 4, 'UNISEX', 'EliteWear', 1603, 2876) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1038-WHT-XS', 1603, 2876 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1038-NAV-L', 1603, 2876 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1038-OLV-XS', 1603, 2876 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1038-SKY-L', 1603, 2876 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 82 FROM v0
UNION ALL
SELECT 1, variant_id, 68 FROM v1
UNION ALL
SELECT 1, variant_id, 62 FROM v2
UNION ALL
SELECT 1, variant_id, 47 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1039', 'Elevated T-Shirts', 4, 'UNISEX', 'DenimPro', 2032, 4742) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1039-SKY-M', 2032, 4742 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1039-OLV-M', 2032, 4742 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1039-BLK-L', 2032, 4742 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 24 FROM v0
UNION ALL
SELECT 1, variant_id, 98 FROM v1
UNION ALL
SELECT 1, variant_id, 80 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1040', 'Elevated T-Shirts', 4, 'UNISEX', 'SmartCasual', 1095, 2083) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1040-BLK-XL', 1095, 2083 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1040-SKY-XL', 1095, 2083 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 84 FROM v0
UNION ALL
SELECT 1, variant_id, 28 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1041', 'Premium T-Shirts', 4, 'UNISEX', 'UrbanEdge', 2426, 4488) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1041-OLV-XS', 2426, 4488 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1041-SKY-XS', 2426, 4488 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 56 FROM v0
UNION ALL
SELECT 1, variant_id, 49 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1042', 'Premium T-Shirts', 4, 'UNISEX', 'SmartCasual', 941, 2331) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1042-OLV-L', 941, 2331 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1042-SKY-XS', 941, 2331 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1042-SKY-L', 941, 2331 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 69 FROM v0
UNION ALL
SELECT 1, variant_id, 37 FROM v1
UNION ALL
SELECT 1, variant_id, 20 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1043', 'Classic T-Shirts', 4, 'UNISEX', 'CasualVibe', 2130, 4023) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1043-OLV-XS', 2130, 4023 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1043-WHT-M', 2130, 4023 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1043-WHT-L', 2130, 4023 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1043-SKY-XL', 2130, 4023 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 96 FROM v0
UNION ALL
SELECT 1, variant_id, 49 FROM v1
UNION ALL
SELECT 1, variant_id, 67 FROM v2
UNION ALL
SELECT 1, variant_id, 17 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1044', 'Dynamic T-Shirts', 4, 'UNISEX', 'DenimPro', 838, 1770) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1044-WHT-XL', 838, 1770 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1044-BLK-L', 838, 1770 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1044-OLV-XS', 838, 1770 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1044-NAV-L', 838, 1770 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 92 FROM v0
UNION ALL
SELECT 1, variant_id, 90 FROM v1
UNION ALL
SELECT 1, variant_id, 29 FROM v2
UNION ALL
SELECT 1, variant_id, 94 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1045', 'Core T-Shirts', 4, 'UNISEX', 'ActiveFit', 1273, 2269) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1045-SKY-M', 1273, 2269 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1045-BLK-L', 1273, 2269 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1045-SKY-XS', 1273, 2269 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1045-BLK-XS', 1273, 2269 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 83 FROM v0
UNION ALL
SELECT 1, variant_id, 61 FROM v1
UNION ALL
SELECT 1, variant_id, 24 FROM v2
UNION ALL
SELECT 1, variant_id, 72 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1046', 'Dynamic T-Shirts', 4, 'UNISEX', 'DenimPro', 1798, 2977) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1046-BLK-S', 1798, 2977 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1046-OLV-XL', 1798, 2977 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1046-SKY-S', 1798, 2977 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1046-SKY-M', 1798, 2977 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 90 FROM v0
UNION ALL
SELECT 1, variant_id, 13 FROM v1
UNION ALL
SELECT 1, variant_id, 54 FROM v2
UNION ALL
SELECT 1, variant_id, 64 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1047', 'Everyday T-Shirts', 4, 'UNISEX', 'SmartCasual', 2059, 4179) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1047-BLK-M', 2059, 4179 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1047-OLV-L', 2059, 4179 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1047-BLK-XS', 2059, 4179 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1047-NAV-XL', 2059, 4179 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 41 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1
UNION ALL
SELECT 1, variant_id, 96 FROM v2
UNION ALL
SELECT 1, variant_id, 47 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1048', 'Premium T-Shirts', 4, 'UNISEX', 'SmartCasual', 1868, 2950) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1048-SKY-L', 1868, 2950 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1048-NAV-XL', 1868, 2950 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1048-BLK-XL', 1868, 2950 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1048-NAV-XS', 1868, 2950 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 12 FROM v0
UNION ALL
SELECT 1, variant_id, 80 FROM v1
UNION ALL
SELECT 1, variant_id, 47 FROM v2
UNION ALL
SELECT 1, variant_id, 79 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1049', 'Dynamic T-Shirts', 4, 'UNISEX', 'SmartCasual', 1167, 1847) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1049-WHT-S', 1167, 1847 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1049-OLV-S', 1167, 1847 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1049-BLK-XL', 1167, 1847 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 36 FROM v0
UNION ALL
SELECT 1, variant_id, 35 FROM v1
UNION ALL
SELECT 1, variant_id, 41 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1050', 'Signature Polo Shirts', 5, 'MEN', 'EliteWear', 2435, 4031) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1050-NAV-S', 2435, 4031 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1050-WHT-M', 2435, 4031 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1050-NAV-XS', 2435, 4031 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1050-OLV-XS', 2435, 4031 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 85 FROM v0
UNION ALL
SELECT 1, variant_id, 53 FROM v1
UNION ALL
SELECT 1, variant_id, 62 FROM v2
UNION ALL
SELECT 1, variant_id, 35 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1051', 'Core Polo Shirts', 5, 'MEN', 'ComfortWear', 2915, 5901) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1051-OLV-S', 2915, 5901 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1051-BLK-S', 2915, 5901 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1051-BLK-M', 2915, 5901 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1051-OLV-XL', 2915, 5901 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 79 FROM v0
UNION ALL
SELECT 1, variant_id, 23 FROM v1
UNION ALL
SELECT 1, variant_id, 32 FROM v2
UNION ALL
SELECT 1, variant_id, 21 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1052', 'Core Polo Shirts', 5, 'MEN', 'ComfortWear', 2951, 5795) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1052-NAV-M', 2951, 5795 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1052-SKY-XL', 2951, 5795 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 51 FROM v0
UNION ALL
SELECT 1, variant_id, 14 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1053', 'Signature Polo Shirts', 5, 'MEN', 'UrbanEdge', 2096, 3175) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1053-WHT-XS', 2096, 3175 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1053-NAV-S', 2096, 3175 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 54 FROM v0
UNION ALL
SELECT 1, variant_id, 49 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1054', 'Urban Polo Shirts', 5, 'MEN', 'SmartCasual', 2143, 4420) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1054-NAV-S', 2143, 4420 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1054-BLK-XS', 2143, 4420 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1054-SKY-XL', 2143, 4420 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 22 FROM v0
UNION ALL
SELECT 1, variant_id, 17 FROM v1
UNION ALL
SELECT 1, variant_id, 20 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1055', 'Classic Polo Shirts', 5, 'MEN', 'DenimPro', 1768, 3726) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1055-BLK-L', 1768, 3726 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1055-OLV-M', 1768, 3726 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1055-BLK-M', 1768, 3726 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1055-NAV-M', 1768, 3726 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 21 FROM v0
UNION ALL
SELECT 1, variant_id, 42 FROM v1
UNION ALL
SELECT 1, variant_id, 39 FROM v2
UNION ALL
SELECT 1, variant_id, 49 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1056', 'Premium Polo Shirts', 5, 'MEN', 'ActiveFit', 1492, 3628) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1056-NAV-XS', 1492, 3628 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1056-BLK-L', 1492, 3628 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1056-OLV-XL', 1492, 3628 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 46 FROM v0
UNION ALL
SELECT 1, variant_id, 51 FROM v1
UNION ALL
SELECT 1, variant_id, 64 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1057', 'Studio Polo Shirts', 5, 'MEN', 'UrbanEdge', 1901, 3704) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1057-SKY-M', 1901, 3704 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1057-NAV-S', 1901, 3704 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 23 FROM v0
UNION ALL
SELECT 1, variant_id, 76 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1058', 'Core Polo Shirts', 5, 'MEN', 'CasualVibe', 1416, 2702) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1058-SKY-S', 1416, 2702 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1058-WHT-S', 1416, 2702 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1058-BLK-XL', 1416, 2702 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1058-BLK-L', 1416, 2702 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 50 FROM v0
UNION ALL
SELECT 1, variant_id, 63 FROM v1
UNION ALL
SELECT 1, variant_id, 49 FROM v2
UNION ALL
SELECT 1, variant_id, 72 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1059', 'Performance Polo Shirts', 5, 'MEN', 'CasualVibe', 1412, 3203) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1059-SKY-L', 1412, 3203 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1059-NAV-XS', 1412, 3203 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 80 FROM v0
UNION ALL
SELECT 1, variant_id, 12 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1060', 'Elevated Polo Shirts', 5, 'MEN', 'UrbanEdge', 2677, 6159) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1060-NAV-XS', 2677, 6159 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1060-WHT-M', 2677, 6159 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 83 FROM v0
UNION ALL
SELECT 1, variant_id, 20 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1061', 'Classic Polo Shirts', 5, 'MEN', 'SmartCasual', 2627, 4855) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1061-NAV-L', 2627, 4855 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1061-SKY-S', 2627, 4855 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1061-BLK-S', 2627, 4855 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 23 FROM v0
UNION ALL
SELECT 1, variant_id, 62 FROM v1
UNION ALL
SELECT 1, variant_id, 72 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1062', 'Classic Polo Shirts', 5, 'MEN', 'EliteWear', 1920, 3610) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1062-WHT-XS', 1920, 3610 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1062-BLK-L', 1920, 3610 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1062-SKY-L', 1920, 3610 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 72 FROM v0
UNION ALL
SELECT 1, variant_id, 58 FROM v1
UNION ALL
SELECT 1, variant_id, 31 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1063', 'Modern Polo Shirts', 5, 'MEN', 'ComfortWear', 2767, 6609) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1063-WHT-XS', 2767, 6609 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1063-OLV-XS', 2767, 6609 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1063-OLV-M', 2767, 6609 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1063-NAV-M', 2767, 6609 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 69 FROM v0
UNION ALL
SELECT 1, variant_id, 92 FROM v1
UNION ALL
SELECT 1, variant_id, 99 FROM v2
UNION ALL
SELECT 1, variant_id, 67 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1064', 'Studio Polo Shirts', 5, 'MEN', 'DenimPro', 2074, 3575) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1064-WHT-M', 2074, 3575 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1064-BLK-XS', 2074, 3575 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1064-WHT-S', 2074, 3575 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1064-WHT-L', 2074, 3575 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 84 FROM v0
UNION ALL
SELECT 1, variant_id, 26 FROM v1
UNION ALL
SELECT 1, variant_id, 74 FROM v2
UNION ALL
SELECT 1, variant_id, 84 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1065', 'Studio Jeans', 7, 'MEN', 'UrbanEdge', 2781, 6380) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1065-NAV-M', 2781, 6380 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1065-OLV-XL', 2781, 6380 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1065-BLK-XL', 2781, 6380 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 77 FROM v0
UNION ALL
SELECT 1, variant_id, 39 FROM v1
UNION ALL
SELECT 1, variant_id, 88 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1066', 'Studio Jeans', 7, 'MEN', 'SmartCasual', 4230, 6977) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1066-SKY-L', 4230, 6977 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1066-WHT-XS', 4230, 6977 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 58 FROM v0
UNION ALL
SELECT 1, variant_id, 59 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1067', 'Studio Jeans', 7, 'MEN', 'CasualVibe', 5070, 11641) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1067-OLV-XS', 5070, 11641 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1067-WHT-M', 5070, 11641 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 16 FROM v0
UNION ALL
SELECT 1, variant_id, 88 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1068', 'Essential Jeans', 7, 'MEN', 'UrbanEdge', 2777, 5612) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1068-NAV-M', 2777, 5612 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1068-WHT-M', 2777, 5612 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1068-WHT-XS', 2777, 5612 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1068-SKY-L', 2777, 5612 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 37 FROM v0
UNION ALL
SELECT 1, variant_id, 78 FROM v1
UNION ALL
SELECT 1, variant_id, 23 FROM v2
UNION ALL
SELECT 1, variant_id, 72 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1069', 'Vintage Jeans', 7, 'MEN', 'DenimPro', 4845, 7928) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1069-WHT-XL', 4845, 7928 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1069-SKY-XL', 4845, 7928 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 17 FROM v0
UNION ALL
SELECT 1, variant_id, 82 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1070', 'Essential Jeans', 7, 'MEN', 'DenimPro', 4680, 7308) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1070-OLV-M', 4680, 7308 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1070-WHT-XL', 4680, 7308 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1070-BLK-M', 4680, 7308 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1070-BLK-XL', 4680, 7308 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 78 FROM v0
UNION ALL
SELECT 1, variant_id, 74 FROM v1
UNION ALL
SELECT 1, variant_id, 98 FROM v2
UNION ALL
SELECT 1, variant_id, 42 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1071', 'Urban Jeans', 7, 'MEN', 'DenimPro', 5432, 9754) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1071-NAV-L', 5432, 9754 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1071-NAV-XS', 5432, 9754 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1071-BLK-M', 5432, 9754 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 82 FROM v0
UNION ALL
SELECT 1, variant_id, 10 FROM v1
UNION ALL
SELECT 1, variant_id, 39 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1072', 'Essential Jeans', 7, 'MEN', 'CasualVibe', 4935, 10869) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1072-SKY-XS', 4935, 10869 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1072-NAV-M', 4935, 10869 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1072-WHT-XS', 4935, 10869 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 38 FROM v0
UNION ALL
SELECT 1, variant_id, 60 FROM v1
UNION ALL
SELECT 1, variant_id, 65 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1073', 'Signature Jeans', 7, 'MEN', 'SmartCasual', 5555, 13355) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1073-NAV-XS', 5555, 13355 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1073-SKY-S', 5555, 13355 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1073-OLV-XS', 5555, 13355 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 13 FROM v0
UNION ALL
SELECT 1, variant_id, 54 FROM v1
UNION ALL
SELECT 1, variant_id, 62 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1074', 'Essential Jeans', 7, 'MEN', 'ActiveFit', 5560, 10211) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1074-OLV-XL', 5560, 10211 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1074-BLK-L', 5560, 10211 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1074-OLV-M', 5560, 10211 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 100 FROM v0
UNION ALL
SELECT 1, variant_id, 87 FROM v1
UNION ALL
SELECT 1, variant_id, 78 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1075', 'Vintage Jeans', 7, 'MEN', 'CasualVibe', 4243, 8452) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1075-OLV-S', 4243, 8452 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1075-WHT-L', 4243, 8452 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1075-BLK-L', 4243, 8452 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1075-OLV-XL', 4243, 8452 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 57 FROM v0
UNION ALL
SELECT 1, variant_id, 74 FROM v1
UNION ALL
SELECT 1, variant_id, 100 FROM v2
UNION ALL
SELECT 1, variant_id, 92 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1076', 'Urban Cotton Pants', 8, 'MEN', 'CasualVibe', 2833, 6846) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1076-OLV-L', 2833, 6846 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1076-OLV-M', 2833, 6846 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1076-WHT-L', 2833, 6846 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1076-WHT-S', 2833, 6846 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 83 FROM v0
UNION ALL
SELECT 1, variant_id, 91 FROM v1
UNION ALL
SELECT 1, variant_id, 61 FROM v2
UNION ALL
SELECT 1, variant_id, 34 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1077', 'Signature Cotton Pants', 8, 'MEN', 'CasualVibe', 4384, 9885) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1077-SKY-M', 4384, 9885 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1077-NAV-L', 4384, 9885 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 38 FROM v0
UNION ALL
SELECT 1, variant_id, 12 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1078', 'Elevated Cotton Pants', 8, 'MEN', 'EliteWear', 3879, 6405) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1078-WHT-XL', 3879, 6405 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1078-OLV-XS', 3879, 6405 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1078-WHT-S', 3879, 6405 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1078-SKY-S', 3879, 6405 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 31 FROM v0
UNION ALL
SELECT 1, variant_id, 66 FROM v1
UNION ALL
SELECT 1, variant_id, 64 FROM v2
UNION ALL
SELECT 1, variant_id, 86 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1079', 'Vintage Cotton Pants', 8, 'MEN', 'DenimPro', 3418, 5561) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1079-WHT-M', 3418, 5561 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1079-NAV-XL', 3418, 5561 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1079-BLK-M', 3418, 5561 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1079-OLV-L', 3418, 5561 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 91 FROM v0
UNION ALL
SELECT 1, variant_id, 32 FROM v1
UNION ALL
SELECT 1, variant_id, 16 FROM v2
UNION ALL
SELECT 1, variant_id, 65 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1080', 'Elevated Cotton Pants', 8, 'MEN', 'DenimPro', 4279, 8867) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1080-WHT-S', 4279, 8867 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1080-OLV-XL', 4279, 8867 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1080-BLK-XL', 4279, 8867 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 99 FROM v0
UNION ALL
SELECT 1, variant_id, 61 FROM v1
UNION ALL
SELECT 1, variant_id, 13 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1081', 'Signature Cotton Pants', 8, 'MEN', 'CasualVibe', 2788, 5695) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1081-BLK-L', 2788, 5695 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1081-BLK-XS', 2788, 5695 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 84 FROM v0
UNION ALL
SELECT 1, variant_id, 32 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1082', 'Core Cotton Pants', 8, 'MEN', 'CasualVibe', 2191, 4298) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1082-SKY-M', 2191, 4298 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1082-WHT-L', 2191, 4298 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1082-BLK-M', 2191, 4298 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1082-NAV-S', 2191, 4298 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 24 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1
UNION ALL
SELECT 1, variant_id, 35 FROM v2
UNION ALL
SELECT 1, variant_id, 27 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1083', 'Essential Cotton Pants', 8, 'MEN', 'EliteWear', 2076, 3819) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1083-WHT-XS', 2076, 3819 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1083-NAV-XL', 2076, 3819 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1083-OLV-L', 2076, 3819 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1083-NAV-L', 2076, 3819 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 35 FROM v0
UNION ALL
SELECT 1, variant_id, 16 FROM v1
UNION ALL
SELECT 1, variant_id, 85 FROM v2
UNION ALL
SELECT 1, variant_id, 83 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1084', 'Classic Cotton Pants', 8, 'MEN', 'ComfortWear', 4298, 6988) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1084-BLK-M', 4298, 6988 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1084-NAV-L', 4298, 6988 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 63 FROM v0
UNION ALL
SELECT 1, variant_id, 15 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1085', 'Signature Cotton Pants', 8, 'MEN', 'SmartCasual', 3358, 6224) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1085-NAV-L', 3358, 6224 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1085-WHT-L', 3358, 6224 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1085-BLK-XL', 3358, 6224 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 81 FROM v0
UNION ALL
SELECT 1, variant_id, 77 FROM v1
UNION ALL
SELECT 1, variant_id, 24 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1086', 'Urban Cotton Pants', 8, 'MEN', 'DenimPro', 3694, 7262) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1086-WHT-M', 3694, 7262 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1086-OLV-M', 3694, 7262 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 51 FROM v0
UNION ALL
SELECT 1, variant_id, 82 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1087', 'Premium Cotton Pants', 8, 'MEN', 'DenimPro', 2212, 3820) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1087-SKY-S', 2212, 3820 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1087-BLK-L', 2212, 3820 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1087-BLK-M', 2212, 3820 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 36 FROM v0
UNION ALL
SELECT 1, variant_id, 66 FROM v1
UNION ALL
SELECT 1, variant_id, 34 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1088', 'Essential Trousers', 9, 'MEN', 'ComfortWear', 4702, 11536) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1088-NAV-L', 4702, 11536 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1088-BLK-XS', 4702, 11536 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1088-NAV-XS', 4702, 11536 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1088-SKY-XL', 4702, 11536 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 47 FROM v0
UNION ALL
SELECT 1, variant_id, 38 FROM v1
UNION ALL
SELECT 1, variant_id, 28 FROM v2
UNION ALL
SELECT 1, variant_id, 53 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1089', 'Performance Trousers', 9, 'MEN', 'SmartCasual', 2859, 5795) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1089-WHT-S', 2859, 5795 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1089-WHT-L', 2859, 5795 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 24 FROM v0
UNION ALL
SELECT 1, variant_id, 84 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1090', 'Core Trousers', 9, 'MEN', 'UrbanEdge', 3441, 7415) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1090-NAV-XS', 3441, 7415 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1090-WHT-S', 3441, 7415 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1090-NAV-M', 3441, 7415 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1090-SKY-M', 3441, 7415 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 56 FROM v0
UNION ALL
SELECT 1, variant_id, 93 FROM v1
UNION ALL
SELECT 1, variant_id, 32 FROM v2
UNION ALL
SELECT 1, variant_id, 54 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1091', 'Everyday Trousers', 9, 'MEN', 'ActiveFit', 4977, 9021) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1091-NAV-S', 4977, 9021 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1091-OLV-XS', 4977, 9021 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1091-BLK-XL', 4977, 9021 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 66 FROM v0
UNION ALL
SELECT 1, variant_id, 45 FROM v1
UNION ALL
SELECT 1, variant_id, 47 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1092', 'Performance Trousers', 9, 'MEN', 'CasualVibe', 4336, 8014) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1092-OLV-S', 4336, 8014 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1092-OLV-XS', 4336, 8014 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 38 FROM v0
UNION ALL
SELECT 1, variant_id, 68 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1093', 'Core Trousers', 9, 'MEN', 'SmartCasual', 3436, 8197) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1093-SKY-XL', 3436, 8197 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1093-WHT-M', 3436, 8197 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1093-SKY-S', 3436, 8197 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 13 FROM v0
UNION ALL
SELECT 1, variant_id, 21 FROM v1
UNION ALL
SELECT 1, variant_id, 49 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1094', 'Dynamic Trousers', 9, 'MEN', 'ActiveFit', 3408, 6926) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1094-BLK-XL', 3408, 6926 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1094-OLV-L', 3408, 6926 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 87 FROM v0
UNION ALL
SELECT 1, variant_id, 64 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1095', 'Everyday Trousers', 9, 'MEN', 'ComfortWear', 2707, 6590) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1095-NAV-M', 2707, 6590 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1095-SKY-L', 2707, 6590 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1095-BLK-S', 2707, 6590 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 11 FROM v0
UNION ALL
SELECT 1, variant_id, 65 FROM v1
UNION ALL
SELECT 1, variant_id, 22 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1096', 'Essential Trousers', 9, 'MEN', 'ComfortWear', 5419, 10637) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1096-OLV-XL', 5419, 10637 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1096-NAV-L', 5419, 10637 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 41 FROM v0
UNION ALL
SELECT 1, variant_id, 62 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1097', 'Core Trousers', 9, 'MEN', 'ActiveFit', 2892, 5792) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1097-WHT-L', 2892, 5792 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1097-SKY-L', 2892, 5792 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1097-NAV-XL', 2892, 5792 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1097-WHT-M', 2892, 5792 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 36 FROM v0
UNION ALL
SELECT 1, variant_id, 46 FROM v1
UNION ALL
SELECT 1, variant_id, 35 FROM v2
UNION ALL
SELECT 1, variant_id, 20 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1098', 'Classic Trousers', 9, 'MEN', 'UrbanEdge', 2528, 4679) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1098-SKY-L', 2528, 4679 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1098-NAV-XL', 2528, 4679 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1098-OLV-L', 2528, 4679 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1098-BLK-S', 2528, 4679 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 24 FROM v0
UNION ALL
SELECT 1, variant_id, 69 FROM v1
UNION ALL
SELECT 1, variant_id, 74 FROM v2
UNION ALL
SELECT 1, variant_id, 10 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1099', 'Urban Trousers', 9, 'MEN', 'ComfortWear', 4235, 10482) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1099-SKY-XL', 4235, 10482 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1099-OLV-XL', 4235, 10482 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1099-WHT-XS', 4235, 10482 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1099-BLK-XL', 4235, 10482 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 53 FROM v0
UNION ALL
SELECT 1, variant_id, 52 FROM v1
UNION ALL
SELECT 1, variant_id, 98 FROM v2
UNION ALL
SELECT 1, variant_id, 40 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1100', 'Studio Shorts', 10, 'MEN', 'ComfortWear', 1811, 2914) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1100-SKY-S', 1811, 2914 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1100-BLK-S', 1811, 2914 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 74 FROM v0
UNION ALL
SELECT 1, variant_id, 86 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1101', 'Vintage Shorts', 10, 'MEN', 'DenimPro', 1138, 1714) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1101-SKY-L', 1138, 1714 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1101-WHT-XS', 1138, 1714 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 92 FROM v0
UNION ALL
SELECT 1, variant_id, 97 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1102', 'Modern Shorts', 10, 'MEN', 'DenimPro', 1697, 3803) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1102-SKY-XS', 1697, 3803 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1102-BLK-XL', 1697, 3803 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 94 FROM v0
UNION ALL
SELECT 1, variant_id, 25 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1103', 'Urban Shorts', 10, 'MEN', 'ComfortWear', 2446, 4655) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1103-BLK-XL', 2446, 4655 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1103-BLK-M', 2446, 4655 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 28 FROM v0
UNION ALL
SELECT 1, variant_id, 17 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1104', 'Essential Shorts', 10, 'MEN', 'ComfortWear', 1083, 2583) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1104-NAV-S', 1083, 2583 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1104-BLK-S', 1083, 2583 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1104-WHT-L', 1083, 2583 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1104-OLV-XL', 1083, 2583 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 65 FROM v0
UNION ALL
SELECT 1, variant_id, 29 FROM v1
UNION ALL
SELECT 1, variant_id, 17 FROM v2
UNION ALL
SELECT 1, variant_id, 81 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1105', 'Elevated Shorts', 10, 'MEN', 'ActiveFit', 1452, 2883) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1105-SKY-XL', 1452, 2883 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1105-WHT-L', 1452, 2883 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1105-OLV-S', 1452, 2883 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1105-SKY-S', 1452, 2883 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 66 FROM v0
UNION ALL
SELECT 1, variant_id, 91 FROM v1
UNION ALL
SELECT 1, variant_id, 35 FROM v2
UNION ALL
SELECT 1, variant_id, 22 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1106', 'Everyday Shorts', 10, 'MEN', 'UrbanEdge', 1766, 4000) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1106-OLV-S', 1766, 4000 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1106-WHT-XS', 1766, 4000 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1106-WHT-L', 1766, 4000 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 35 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1
UNION ALL
SELECT 1, variant_id, 67 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1107', 'Everyday Shorts', 10, 'MEN', 'ComfortWear', 1016, 1691) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1107-OLV-M', 1016, 1691 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1107-OLV-L', 1016, 1691 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 45 FROM v0
UNION ALL
SELECT 1, variant_id, 89 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1108', 'Classic Shorts', 10, 'MEN', 'ComfortWear', 1935, 4442) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1108-BLK-S', 1935, 4442 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1108-NAV-L', 1935, 4442 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1108-SKY-S', 1935, 4442 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1108-OLV-L', 1935, 4442 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 40 FROM v0
UNION ALL
SELECT 1, variant_id, 41 FROM v1
UNION ALL
SELECT 1, variant_id, 69 FROM v2
UNION ALL
SELECT 1, variant_id, 70 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1109', 'Signature Shorts', 10, 'MEN', 'SmartCasual', 2111, 3204) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1109-NAV-XL', 2111, 3204 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1109-SKY-XL', 2111, 3204 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1109-SKY-M', 2111, 3204 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 95 FROM v0
UNION ALL
SELECT 1, variant_id, 54 FROM v1
UNION ALL
SELECT 1, variant_id, 88 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1110', 'Essential Shorts', 10, 'MEN', 'EliteWear', 1966, 3759) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1110-NAV-XS', 1966, 3759 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1110-OLV-XL', 1966, 3759 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1110-SKY-S', 1966, 3759 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1110-OLV-L', 1966, 3759 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 29 FROM v0
UNION ALL
SELECT 1, variant_id, 84 FROM v1
UNION ALL
SELECT 1, variant_id, 43 FROM v2
UNION ALL
SELECT 1, variant_id, 33 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1111', 'Urban Shorts', 10, 'MEN', 'EliteWear', 1355, 2658) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1111-BLK-M', 1355, 2658 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1111-WHT-M', 1355, 2658 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1111-NAV-M', 1355, 2658 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1111-OLV-XL', 1355, 2658 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 10 FROM v0
UNION ALL
SELECT 1, variant_id, 97 FROM v1
UNION ALL
SELECT 1, variant_id, 21 FROM v2
UNION ALL
SELECT 1, variant_id, 94 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1112', 'Signature Cargo Pants', 11, 'MEN', 'EliteWear', 2995, 6057) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1112-WHT-L', 2995, 6057 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1112-WHT-M', 2995, 6057 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1112-BLK-XL', 2995, 6057 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1112-WHT-S', 2995, 6057 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 40 FROM v0
UNION ALL
SELECT 1, variant_id, 28 FROM v1
UNION ALL
SELECT 1, variant_id, 17 FROM v2
UNION ALL
SELECT 1, variant_id, 56 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1113', 'Studio Cargo Pants', 11, 'MEN', 'UrbanEdge', 2759, 5495) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1113-WHT-L', 2759, 5495 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1113-OLV-XL', 2759, 5495 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1113-NAV-XL', 2759, 5495 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 96 FROM v0
UNION ALL
SELECT 1, variant_id, 20 FROM v1
UNION ALL
SELECT 1, variant_id, 75 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1114', 'Everyday Cargo Pants', 11, 'MEN', 'DenimPro', 2172, 4212) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1114-SKY-XS', 2172, 4212 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1114-BLK-S', 2172, 4212 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 92 FROM v0
UNION ALL
SELECT 1, variant_id, 39 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1115', 'Urban Cargo Pants', 11, 'MEN', 'UrbanEdge', 3278, 6348) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1115-NAV-S', 3278, 6348 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1115-BLK-M', 3278, 6348 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1115-BLK-L', 3278, 6348 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1115-BLK-S', 3278, 6348 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 67 FROM v0
UNION ALL
SELECT 1, variant_id, 78 FROM v1
UNION ALL
SELECT 1, variant_id, 33 FROM v2
UNION ALL
SELECT 1, variant_id, 91 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1116', 'Urban Cargo Pants', 11, 'MEN', 'SmartCasual', 3297, 8107) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1116-WHT-S', 3297, 8107 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1116-BLK-L', 3297, 8107 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 100 FROM v0
UNION ALL
SELECT 1, variant_id, 12 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1117', 'Elevated Cargo Pants', 11, 'MEN', 'DenimPro', 2291, 5652) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1117-WHT-S', 2291, 5652 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1117-NAV-S', 2291, 5652 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 71 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1118', 'Classic Cargo Pants', 11, 'MEN', 'ComfortWear', 3564, 6717) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1118-BLK-L', 3564, 6717 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1118-NAV-M', 3564, 6717 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1118-SKY-XS', 3564, 6717 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 99 FROM v0
UNION ALL
SELECT 1, variant_id, 83 FROM v1
UNION ALL
SELECT 1, variant_id, 23 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1119', 'Modern Cargo Pants', 11, 'MEN', 'ComfortWear', 3951, 8836) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1119-BLK-L', 3951, 8836 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1119-WHT-XL', 3951, 8836 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 45 FROM v0
UNION ALL
SELECT 1, variant_id, 48 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1120', 'Dynamic Cargo Pants', 11, 'MEN', 'DenimPro', 2345, 4521) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1120-WHT-M', 2345, 4521 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1120-WHT-XS', 2345, 4521 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1120-NAV-S', 2345, 4521 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1120-OLV-M', 2345, 4521 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 52 FROM v0
UNION ALL
SELECT 1, variant_id, 87 FROM v1
UNION ALL
SELECT 1, variant_id, 65 FROM v2
UNION ALL
SELECT 1, variant_id, 52 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1121', 'Premium Cargo Pants', 11, 'MEN', 'DenimPro', 2400, 5923) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1121-SKY-L', 2400, 5923 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1121-OLV-XL', 2400, 5923 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1121-OLV-XS', 2400, 5923 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 96 FROM v0
UNION ALL
SELECT 1, variant_id, 43 FROM v1
UNION ALL
SELECT 1, variant_id, 40 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1122', 'Signature Gym Wear', 13, 'UNISEX', 'CasualVibe', 2992, 4899) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1122-BLK-XS', 2992, 4899 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1122-WHT-L', 2992, 4899 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 11 FROM v0
UNION ALL
SELECT 1, variant_id, 19 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1123', 'Vintage Gym Wear', 13, 'UNISEX', 'CasualVibe', 1496, 2717) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1123-BLK-XL', 1496, 2717 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1123-BLK-M', 1496, 2717 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 76 FROM v0
UNION ALL
SELECT 1, variant_id, 65 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1124', 'Studio Gym Wear', 13, 'UNISEX', 'SmartCasual', 1097, 2318) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1124-SKY-S', 1097, 2318 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1124-WHT-M', 1097, 2318 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1124-OLV-XS', 1097, 2318 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1124-WHT-L', 1097, 2318 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 87 FROM v0
UNION ALL
SELECT 1, variant_id, 73 FROM v1
UNION ALL
SELECT 1, variant_id, 55 FROM v2
UNION ALL
SELECT 1, variant_id, 53 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1125', 'Essential Gym Wear', 13, 'UNISEX', 'SmartCasual', 1089, 2466) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1125-SKY-L', 1089, 2466 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1125-SKY-S', 1089, 2466 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1125-SKY-M', 1089, 2466 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 58 FROM v0
UNION ALL
SELECT 1, variant_id, 63 FROM v1
UNION ALL
SELECT 1, variant_id, 93 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1126', 'Vintage Gym Wear', 13, 'UNISEX', 'ComfortWear', 1598, 2786) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1126-BLK-L', 1598, 2786 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1126-OLV-XL', 1598, 2786 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1126-OLV-L', 1598, 2786 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1126-OLV-S', 1598, 2786 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 85 FROM v0
UNION ALL
SELECT 1, variant_id, 83 FROM v1
UNION ALL
SELECT 1, variant_id, 75 FROM v2
UNION ALL
SELECT 1, variant_id, 47 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1127', 'Dynamic Gym Wear', 13, 'UNISEX', 'EliteWear', 2111, 3780) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1127-NAV-S', 2111, 3780 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1127-SKY-S', 2111, 3780 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 26 FROM v0
UNION ALL
SELECT 1, variant_id, 85 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1128', 'Dynamic Gym Wear', 13, 'UNISEX', 'CasualVibe', 1541, 3728) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1128-NAV-XL', 1541, 3728 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1128-SKY-L', 1541, 3728 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1128-OLV-S', 1541, 3728 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1128-WHT-L', 1541, 3728 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 52 FROM v0
UNION ALL
SELECT 1, variant_id, 81 FROM v1
UNION ALL
SELECT 1, variant_id, 61 FROM v2
UNION ALL
SELECT 1, variant_id, 12 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1129', 'Everyday Gym Wear', 13, 'UNISEX', 'UrbanEdge', 1840, 2772) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1129-SKY-M', 1840, 2772 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1129-SKY-S', 1840, 2772 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1129-OLV-M', 1840, 2772 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 26 FROM v0
UNION ALL
SELECT 1, variant_id, 89 FROM v1
UNION ALL
SELECT 1, variant_id, 10 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1130', 'Vintage Gym Wear', 13, 'UNISEX', 'SmartCasual', 2947, 7203) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1130-SKY-S', 2947, 7203 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1130-BLK-XL', 2947, 7203 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1130-WHT-S', 2947, 7203 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 99 FROM v0
UNION ALL
SELECT 1, variant_id, 33 FROM v1
UNION ALL
SELECT 1, variant_id, 67 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1131', 'Core Gym Wear', 13, 'UNISEX', 'SmartCasual', 2361, 4587) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1131-OLV-XL', 2361, 4587 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1131-SKY-XS', 2361, 4587 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1131-WHT-S', 2361, 4587 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 52 FROM v0
UNION ALL
SELECT 1, variant_id, 50 FROM v1
UNION ALL
SELECT 1, variant_id, 45 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1132', 'Essential Track Pants', 14, 'UNISEX', 'EliteWear', 2787, 4437) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1132-NAV-L', 2787, 4437 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1132-NAV-XL', 2787, 4437 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1132-NAV-S', 2787, 4437 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1132-SKY-S', 2787, 4437 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 94 FROM v0
UNION ALL
SELECT 1, variant_id, 84 FROM v1
UNION ALL
SELECT 1, variant_id, 47 FROM v2
UNION ALL
SELECT 1, variant_id, 92 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1133', 'Urban Track Pants', 14, 'UNISEX', 'UrbanEdge', 3100, 6830) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 2, 'ART-1133-NAV-S', 3100, 6830 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1133-NAV-XS', 3100, 6830 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 3, 'ART-1133-SKY-M', 3100, 6830 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1133-SKY-XS', 3100, 6830 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 75 FROM v0
UNION ALL
SELECT 1, variant_id, 91 FROM v1
UNION ALL
SELECT 1, variant_id, 61 FROM v2
UNION ALL
SELECT 1, variant_id, 96 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1134', 'Studio Track Pants', 14, 'UNISEX', 'CasualVibe', 3085, 6970) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1134-OLV-M', 3085, 6970 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1134-NAV-XL', 3085, 6970 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 4, 'ART-1134-SKY-L', 3085, 6970 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1134-WHT-XS', 3085, 6970 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 77 FROM v0
UNION ALL
SELECT 1, variant_id, 77 FROM v1
UNION ALL
SELECT 1, variant_id, 94 FROM v2
UNION ALL
SELECT 1, variant_id, 29 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1135', 'Signature Track Pants', 14, 'UNISEX', 'EliteWear', 2927, 4876) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1135-OLV-S', 2927, 4876 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1135-SKY-S', 2927, 4876 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 28 FROM v0
UNION ALL
SELECT 1, variant_id, 30 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1136', 'Everyday Track Pants', 14, 'UNISEX', 'CasualVibe', 2275, 4904) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 2, 'ART-1136-WHT-S', 2275, 4904 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1136-SKY-XS', 2275, 4904 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 3, 'ART-1136-OLV-M', 2275, 4904 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1136-OLV-XL', 2275, 4904 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 29 FROM v0
UNION ALL
SELECT 1, variant_id, 12 FROM v1
UNION ALL
SELECT 1, variant_id, 41 FROM v2
UNION ALL
SELECT 1, variant_id, 83 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1137', 'Performance Track Pants', 14, 'UNISEX', 'ComfortWear', 1626, 3520) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1137-BLK-XL', 1626, 3520 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 3, 'ART-1137-NAV-M', 1626, 3520 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1137-SKY-S', 1626, 3520 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1137-SKY-XL', 1626, 3520 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 10 FROM v0
UNION ALL
SELECT 1, variant_id, 57 FROM v1
UNION ALL
SELECT 1, variant_id, 50 FROM v2
UNION ALL
SELECT 1, variant_id, 69 FROM v3;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1138', 'Classic Track Pants', 14, 'UNISEX', 'EliteWear', 1900, 3991) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1138-SKY-XL', 1900, 3991 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1138-NAV-L', 1900, 3991 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 25 FROM v0
UNION ALL
SELECT 1, variant_id, 76 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1139', 'Dynamic Track Pants', 14, 'UNISEX', 'ComfortWear', 1754, 3265) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1139-WHT-L', 1754, 3265 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1139-BLK-S', 1754, 3265 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1139-WHT-M', 1754, 3265 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 72 FROM v0
UNION ALL
SELECT 1, variant_id, 99 FROM v1
UNION ALL
SELECT 1, variant_id, 33 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1140', 'Performance Track Pants', 14, 'UNISEX', 'ActiveFit', 3030, 5072) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1140-BLK-M', 3030, 5072 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1140-SKY-XL', 3030, 5072 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 3, 'ART-1140-WHT-M', 3030, 5072 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 89 FROM v0
UNION ALL
SELECT 1, variant_id, 40 FROM v1
UNION ALL
SELECT 1, variant_id, 45 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1141', 'Vintage Track Pants', 14, 'UNISEX', 'CasualVibe', 2881, 6208) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 5, 'ART-1141-WHT-XL', 2881, 6208 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1141-NAV-XS', 2881, 6208 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1141-BLK-M', 2881, 6208 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 92 FROM v0
UNION ALL
SELECT 1, variant_id, 98 FROM v1
UNION ALL
SELECT 1, variant_id, 19 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1142', 'Essential Hoodies', 15, 'UNISEX', 'ComfortWear', 5379, 11927) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1142-SKY-S', 5379, 11927 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 3, 'ART-1142-BLK-M', 5379, 11927 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 98 FROM v0
UNION ALL
SELECT 1, variant_id, 96 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1143', 'Signature Hoodies', 15, 'UNISEX', 'EliteWear', 2810, 4602) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1143-OLV-XS', 2810, 4602 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1143-SKY-S', 2810, 4602 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 44 FROM v0
UNION ALL
SELECT 1, variant_id, 81 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1144', 'Signature Hoodies', 15, 'UNISEX', 'CasualVibe', 3574, 6323) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1144-WHT-L', 3574, 6323 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1144-OLV-XS', 3574, 6323 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 71 FROM v0
UNION ALL
SELECT 1, variant_id, 74 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1145', 'Modern Hoodies', 15, 'UNISEX', 'CasualVibe', 3456, 5473) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 4, 'ART-1145-NAV-L', 3456, 5473 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1145-OLV-XL', 3456, 5473 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 2, 'ART-1145-SKY-S', 3456, 5473 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 96 FROM v0
UNION ALL
SELECT 1, variant_id, 86 FROM v1
UNION ALL
SELECT 1, variant_id, 74 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1146', 'Urban Hoodies', 15, 'UNISEX', 'SmartCasual', 2609, 4041) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 4, 'ART-1146-OLV-L', 2609, 4041 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 5, 'ART-1146-OLV-XL', 2609, 4041 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 86 FROM v0
UNION ALL
SELECT 1, variant_id, 11 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1147', 'Core Hoodies', 15, 'UNISEX', 'CasualVibe', 4562, 7425) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1147-BLK-XS', 4562, 7425 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 5, 'ART-1147-NAV-XL', 4562, 7425 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1147-WHT-L', 4562, 7425 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 71 FROM v0
UNION ALL
SELECT 1, variant_id, 27 FROM v1
UNION ALL
SELECT 1, variant_id, 37 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1148', 'Elevated Hoodies', 15, 'UNISEX', 'ActiveFit', 5593, 9152) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 4, 'ART-1148-BLK-L', 5593, 9152 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 5, 'ART-1148-SKY-XL', 5593, 9152 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 28 FROM v0
UNION ALL
SELECT 1, variant_id, 37 FROM v1;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1149', 'Signature Hoodies', 15, 'UNISEX', 'CasualVibe', 4367, 7301) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 5, 'ART-1149-BLK-XL', 4367, 7301 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 2, 'ART-1149-BLK-S', 4367, 7301 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 4, 'ART-1149-WHT-L', 4367, 7301 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 47 FROM v0
UNION ALL
SELECT 1, variant_id, 62 FROM v1
UNION ALL
SELECT 1, variant_id, 99 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1150', 'Dynamic Hoodies', 15, 'UNISEX', 'ComfortWear', 3338, 6388) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 2, 1, 'ART-1150-WHT-XS', 3338, 6388 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 1, 'ART-1150-OLV-XS', 3338, 6388 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1150-NAV-XS', 3338, 6388 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 25 FROM v0
UNION ALL
SELECT 1, variant_id, 90 FROM v1
UNION ALL
SELECT 1, variant_id, 34 FROM v2;

WITH p AS (INSERT INTO clothing_store.products (article_code, product_name, category_id, gender, brand, base_cost_price, base_selling_price) VALUES ('ART-1151', 'Core Hoodies', 15, 'UNISEX', 'CasualVibe', 5079, 9624) RETURNING product_id),
v0 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 4, 1, 'ART-1151-SKY-XS', 5079, 9624 FROM p RETURNING variant_id),
v1 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 5, 2, 'ART-1151-OLV-S', 5079, 9624 FROM p RETURNING variant_id),
v2 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 3, 1, 'ART-1151-NAV-XS', 5079, 9624 FROM p RETURNING variant_id),
v3 AS (INSERT INTO clothing_store.product_variants (product_id, color_id, size_id, sku, cost_price, selling_price) SELECT product_id, 1, 1, 'ART-1151-BLK-XS', 5079, 9624 FROM p RETURNING variant_id)
INSERT INTO clothing_store.branch_inventory (branch_id, variant_id, quantity_on_hand)
SELECT 1, variant_id, 46 FROM v0
UNION ALL
SELECT 1, variant_id, 43 FROM v1
UNION ALL
SELECT 1, variant_id, 36 FROM v2
UNION ALL
SELECT 1, variant_id, 37 FROM v3;

COMMIT;