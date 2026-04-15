import asyncio
from tortoise import Tortoise
from models import User, Car, UserCar
# from models import User
# from tortoise.connection import connections


async def init():
    await Tortoise.init(db_url="sqlite://database.db", modules={"models": ['models']})
    await Tortoise.generate_schemas()
    print('database connection open')

# async def UserInfo(id):
#     user = await User.get(id=id).prefetch_related("user_cars__car")
#     return user

async def UserExist(id):
    exist = await User.filter(id=id).exists()
    # print(exist)
    return exist

async def AddUser(id, username, fullname, chat_id):
    user = await User.create(id=id, username=username, fullname=fullname, chat_id=chat_id)
    return user

# простая первая версия
# надо сделать с видами сортировки 
# возможно добавить страницы типо первые 10 вторые 10 и так далее
# можно вместить gtop и обыч top в одну функцию через передачу параметра и if 
async def GTopUsers():
    users = await User.all().order_by("-lvl").limit(10)
    return users

async def GetUser(id):
    user = await User.get_or_none(id=id).prefetch_related("user_cars__car")
    print(user, user.fullname())
    return user