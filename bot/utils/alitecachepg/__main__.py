import asyncio
from core.core import create_caching_pool
import os


async def main():
    pool = await create_caching_pool(dsn=os.getenv("DATABASE_URL"))
    print(await pool.fetch("SELECT * FROM prefixes"))


asyncio.run(main())
