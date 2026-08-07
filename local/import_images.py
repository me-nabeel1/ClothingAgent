import asyncio
import csv
import sys
import os

# Add clothing_app to python path to import app.database and models
sys.path.insert(0, os.path.abspath("clothing_app"))

from sqlalchemy import text
from app.database import get_session_factory

async def main():
    session_factory = get_session_factory()
    async with session_factory() as session:
        # Clear existing images
        await session.execute(text("DELETE FROM clothing_store.product_images"))
        print("Cleared existing product_images.")
        
        # Load colors into a dictionary for fast lookup
        result = await session.execute(text("SELECT color_id, color_name FROM clothing_store.colors"))
        colors = {row[1].lower(): row[0] for row in result.fetchall()}
        
        with open("local/unsplash_product_variant_links.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                product_id = int(row["product_id"])
                color_name = row["color_variant"].lower()
                is_primary = row["is_primary"].lower() == "true"
                url = row["unsplash_photo_url"]
                alt_text = row["photo_title"]
                
                color_id = colors.get(color_name)
                if not color_id:
                    print(f"Color '{color_name}' not found. Creating it...")
                    # Generate a hex color (just a dummy one)
                    await session.execute(
                        text("""
                            INSERT INTO clothing_store.colors (color_name, color_code, hex_code)
                            VALUES (:name, :code, :hex)
                        """),
                        {"name": row["color_variant"].title(), "code": color_name.replace(' ', '_'), "hex": "#888888"}
                    )
                    # Fetch the new ID
                    res = await session.execute(text("SELECT color_id FROM clothing_store.colors WHERE color_code = :code"), {"code": color_name.replace(' ', '_')})
                    color_id = res.fetchone()[0]
                    colors[color_name] = color_id
                    
                await session.execute(
                    text("""
                        INSERT INTO clothing_store.product_images 
                        (product_id, color_id, image_path, alt_text, display_order, is_primary)
                        VALUES (:product_id, :color_id, :image_path, :alt_text, :display_order, :is_primary)
                    """),
                    {
                        "product_id": product_id,
                        "color_id": color_id,
                        "image_path": url,
                        "alt_text": alt_text,
                        "display_order": 0,
                        "is_primary": is_primary
                    }
                )
                
        await session.commit()
        print("Successfully imported images from CSV")

if __name__ == "__main__":
    asyncio.run(main())
