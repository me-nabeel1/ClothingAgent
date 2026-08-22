"""Destructive local-demo database reset helper.

Use Alembic plus ``clothing_app/scripts/seed.py`` after this command to rebuild the
schema and Northstar demo data.
"""
from __future__ import annotations
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "clothing_app"))

from app.config import get_config
from app.database import get_engine


async def main() -> None:
    """Drop the demo schema using the configured database connection."""
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS clothing_store CASCADE"))
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
