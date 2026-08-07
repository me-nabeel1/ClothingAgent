import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("clothing_app"))
from sqlalchemy import text
from app.database import get_session_factory

async def main():
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(text("SELECT c.color_name, pv.product_id FROM clothing_store.product_variants pv JOIN clothing_store.colors c ON pv.color_id = c.color_id WHERE pv.product_id IN (1, 2, 3)"))
        for row in result.fetchall():
            print(row)

if __name__ == "__main__":
    asyncio.run(main())
