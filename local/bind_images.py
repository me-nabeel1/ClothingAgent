import random

# Map categories to the filenames available in local/product_images/
cat_images = {
    2: ["monarch_mandarin_collar_beige.webp", "monarch_mandarin_collar_shirt_cream.webp", "regent_oxford_formal_shirt_white.webp"],
    3: ["breeze_short_sleeve_shirt_peach.webp", "breeze_short_sleeve_shirt_sand.webp", "essential_cotton_button_down_pale_blue.webp", "harbor_linen_blend_shirt_light_blue.webp"],
    4: ["city_grid_graphic_tshirt_black.webp", "city_grid_graphic_tshirt_charcoal.webp", "core_crew_neck_tshirt_lightgray.webp", "core_crew_neck_tshirt_white.webp", "limited_drop_neon_tee_lime.webp", "limited_drop_neon_tee_neon_green.webp"],
    5: ["heritage_pique_polo_navy_blue.webp"],
    7: ["foundry_straight_jeans_dark_blue.webp", "ridge_slim_fit_jeans_medium_blue.webp"],
    8: ["avenue_cotton_chinos_khaki.webp", "classic_cotton_pants_brown.webp", "classic_cotton_pants_taupe.webp"],
    9: ["comfort_stretch_trousers_charcoal_gray.webp", "executive_pleated_trousers_black.webp", "studio_drawstring_trousers_stone.webp", "studio_drawstring_trousers_taupe.webp"],
    10: ["motion_training_shorts_black.webp", "motion_training_shorts_charcoal.webp", "motion_training_shorts_teal.webp", "weekend_denim_shorts_medium_blue.webp"],
    11: ["utility_six_pocket_cargo_olive_green.webp"],
    13: ["flex_compression_tee_black.webp", "flex_compression_tee_blue.webp", "velocity_training_tshirt_black.webp", "velocity_training_tshirt_navy.webp", "velocity_training_tshirt_teal.webp"],
    14: ["aero_gym_joggers_dark_gray.webp", "sprint_tapered_track_pants_black.webp", "sprint_tapered_track_pants_charcoal.webp", "sprint_tapered_track_pants_teal.webp"],
    15: ["metro_fleece_hoodie_burgundy.webp", "metro_fleece_hoodie_maroon.webp"]
}

sql_lines = ["BEGIN;"]

# Generate SQL to insert a random image for every product >= 25
for p_id in range(25, 202):
    # This CTE gets the category of the product, and we assign an image randomly in python based on the assumed category. 
    # But wait, python doesn't know the category of product_id=25 without querying.
    # Instead, we can write a SQL DO block!
    pass

# Writing a pure SQL block is better
sql = """
DO $$
DECLARE
    rec RECORD;
    img_name TEXT;
BEGIN
    FOR rec IN SELECT product_id, category_id FROM clothing_store.products WHERE product_id >= 25 LOOP
        CASE rec.category_id
            WHEN 2 THEN
                img_name := (ARRAY['monarch_mandarin_collar_beige.webp', 'monarch_mandarin_collar_shirt_cream.webp', 'regent_oxford_formal_shirt_white.webp'])[floor(random() * 3 + 1)];
            WHEN 3 THEN
                img_name := (ARRAY['breeze_short_sleeve_shirt_peach.webp', 'breeze_short_sleeve_shirt_sand.webp', 'essential_cotton_button_down_pale_blue.webp', 'harbor_linen_blend_shirt_light_blue.webp'])[floor(random() * 4 + 1)];
            WHEN 4 THEN
                img_name := (ARRAY['city_grid_graphic_tshirt_black.webp', 'city_grid_graphic_tshirt_charcoal.webp', 'core_crew_neck_tshirt_lightgray.webp', 'core_crew_neck_tshirt_white.webp', 'limited_drop_neon_tee_lime.webp', 'limited_drop_neon_tee_neon_green.webp'])[floor(random() * 6 + 1)];
            WHEN 5 THEN
                img_name := 'heritage_pique_polo_navy_blue.webp';
            WHEN 7 THEN
                img_name := (ARRAY['foundry_straight_jeans_dark_blue.webp', 'ridge_slim_fit_jeans_medium_blue.webp'])[floor(random() * 2 + 1)];
            WHEN 8 THEN
                img_name := (ARRAY['avenue_cotton_chinos_khaki.webp', 'classic_cotton_pants_brown.webp', 'classic_cotton_pants_taupe.webp'])[floor(random() * 3 + 1)];
            WHEN 9 THEN
                img_name := (ARRAY['comfort_stretch_trousers_charcoal_gray.webp', 'executive_pleated_trousers_black.webp', 'studio_drawstring_trousers_stone.webp', 'studio_drawstring_trousers_taupe.webp'])[floor(random() * 4 + 1)];
            WHEN 10 THEN
                img_name := (ARRAY['motion_training_shorts_black.webp', 'motion_training_shorts_charcoal.webp', 'motion_training_shorts_teal.webp', 'weekend_denim_shorts_medium_blue.webp'])[floor(random() * 4 + 1)];
            WHEN 11 THEN
                img_name := 'utility_six_pocket_cargo_olive_green.webp';
            WHEN 13 THEN
                img_name := (ARRAY['flex_compression_tee_black.webp', 'flex_compression_tee_blue.webp', 'velocity_training_tshirt_black.webp', 'velocity_training_tshirt_navy.webp', 'velocity_training_tshirt_teal.webp'])[floor(random() * 5 + 1)];
            WHEN 14 THEN
                img_name := (ARRAY['aero_gym_joggers_dark_gray.webp', 'sprint_tapered_track_pants_black.webp', 'sprint_tapered_track_pants_charcoal.webp', 'sprint_tapered_track_pants_teal.webp'])[floor(random() * 4 + 1)];
            WHEN 15 THEN
                img_name := (ARRAY['metro_fleece_hoodie_burgundy.webp', 'metro_fleece_hoodie_maroon.webp'])[floor(random() * 2 + 1)];
            ELSE
                img_name := 'core_crew_neck_tshirt_white.webp'; -- fallback
        END CASE;

        INSERT INTO clothing_store.product_images (product_id, image_path, is_primary)
        VALUES (rec.product_id, img_name, true);
    END LOOP;
END $$;
"""

with open("local/bind_images.sql", "w", encoding="utf-8") as f:
    f.write(sql)
