import asyncio
from tortoise import Tortoise


async def init():
    await Tortoise.init(db_url="sqlite://database.db", modules={"models": ['models']})
    await Tortoise.generate_schemas()
    print('database connection open')