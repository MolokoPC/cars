import asyncio
from tortoise import Tortoise
from models import User, Car, UserCar
from tortoise.functions import Count
# from models import User
# from tortoise.connection import connections


async def init():
    await Tortoise.init(db_url="sqlite://database.db", modules={"models": ['models']})
    await Tortoise.generate_schemas()
    print('database connection open')

# async def UserInfo(id):
#     user = await User.get(id=id).prefetch_related("user_cars__car")
#     return user


# проверка есть ли запись пользователя в базе 
# работает вроде нормально но не знаю наверное нет (тут все работает через жопу)
async def UserExist(id):
    exist = await User.filter(id=id).exists()
    return exist

# добавляет нового пользователя
# надо переделать на create or get или как там его 
# для того чтобы выгладило красивее и меньше запросов 
# но незн 50 на 50 думать надо
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

# выдача user с подрузом UserCar модели Car
# если ты не тупой поймешь 
async def GetUser(id):
    user = await User.get_or_none(id=id).prefetch_related("user_cars__car")
    print(user, user.fullname)
    return user


# просто выдает все машины без ничего лишнего (без подгрузки связей)
async def GetCars():
    cars = await Car.all()
    return cars

# выдает список с словарями такого формата {"rarity": <CarRarity....>, "count": count}
async def GetCarsRarity():
    cars_rarity = await Car.annotate(count=Count("id")).group_by("rarity").values("rarity", "count")
    return cars_rarity