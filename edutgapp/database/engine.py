import asyncio
import asyncpg

from decouple import config
from contextlib import asynccontextmanager

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=config("SQL_URL"))
        print("Пул соединений установлен")

    async def close(self):
        await self.pool.close()
        print("Пул соединений закрыт")

    async def fetch(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    async def fetchval(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, *args)
        except Exception as e:
            print(f"Error fetching value: {e}")
            return None  

    async def fetchrow(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except Exception as e:
            print(f"Error fetching row: {e}")
            return None  

    async def execute(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        except Exception as e:
            print(f"Error executing query: {e}")
            return None 

    @asynccontextmanager
    async def transaction(self):
        conn = await self.pool.acquire()
        try:
            async with conn.transaction():
                yield conn
        except Exception as e:
            print(f"Error during transaction: {e}")
            raise  
        finally:
            await self.pool.release(conn)


db = Database()


# async def connect_to_db():
#     conn = await asyncpg.connect(config("SQL_URL"))
#     print("Подключение установлено")

#     return conn


# async def close_db_connection(conn):
#     await conn.close()
#     print("Соединение закрыто")


# async def run_queries():
#     conn = await connect_to_db()



# asyncio.run(run_queries())