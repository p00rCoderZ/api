import asyncio
import asyncpg

class Db:
    _pool = None
    
    @staticmethod
    async def init(dsn):
        Db._pool = await asyncpg.create_pool(dsn=dsn)

    @staticmethod
    def get_pool():
        return Db._pool
