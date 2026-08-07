import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("clothing_app"))
from sqlalchemy import text
from app.database import get_session_factory

async def main():
    session_factory = get_session_factory()
    async with session_factory() as session:
        result = await session.execute(text("SELECT color_name FROM clothing_store.colors"))
        print([row[0] for row in result.fetchall()])

if __name__ == "__main__":
    asyncio.run(main())
