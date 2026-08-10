import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect('postgresql://postgres:pgadmin@127.0.0.1:5432/ClothingAppDummyDB')
    await conn.execute('DROP SCHEMA IF EXISTS clothing_store CASCADE;')
    await conn.execute('DROP TABLE IF EXISTS alembic_version CASCADE;')
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
