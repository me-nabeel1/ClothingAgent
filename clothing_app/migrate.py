import asyncio
import sys
from pathlib import Path

# Ensure the app module is in path
workspace_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(workspace_root))

from sqlalchemy import text

from clothing_app.app.database import get_engine


async def main():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE clothing_store.product_images ADD COLUMN IF NOT EXISTS color_id INTEGER REFERENCES clothing_store.colors(color_id) ON DELETE CASCADE;"))
    print("Migration complete")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
