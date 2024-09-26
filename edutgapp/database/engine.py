import asyncio
import asyncpg

from decouple import config
from database import requests


async def connect_to_db():
    conn = await asyncpg.connect(config("SQL_URL"))
    print("Подключение установлено")

    return conn


async def close_db_connection(conn):
    await conn.close()
    print("Соединение закрыто")


async def run_queries():
    conn = await connect_to_db()


async def choose_lvl():
    conn = await connect_to_db()
    rows = await conn.fetch("SELECT * FROM Level")
    return rows


async def student_levels():
    
    conn = await connect_to_db()
    rows = await choose_lvl()

    temp = []
    for row in rows:
        temp.append(row["eng_lvl"])
    return temp



asyncio.run(run_queries())