import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from tortoise import Tortoise


# from database import *
from models import CarRarity, User, UserCar, Car
from funcs import init

# Загружаем переменные из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

help_text = """
/help - это сообщение
/start - начать игру
/top - топ игроков
/gtop - глобальный топ игроков
/profile - просмотр профиля
/car - 
/shop - 
"""

GTop_text_template = """
Глобальный топ:
""" 

Profile_text_template = """
{}
`··············`
{} из {} машин
{} уровень
`··············`
Обычных: {} из {}
Редких: {} из {}
Сверхредких: {} из {}
Эпических: {} из {}
Мифических: {} из {}
Легендарных: {} из {}
`··············`
{} pts
"""

Cars_text_template = """
**{}**  
> {} машина
{} из {} • {}\!  
`··············`  
_\+{} pts_
"""



# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



# Обработчик команды /start и добавление в игру 
# добавить добавления ко всем и наверное лучше через create or get
# в создание/проверку пользователя передавать message
@dp.message(Command("start"))
async def command_start_handler(message: types.Message):
    id = message.from_user.id
    chat_id = message.chat.id
    fullname = message.from_user.full_name
    username = message.from_user.username

    if await User.UserExist(id):
        await message.answer(f"Привет, {fullname}! Вы уже в игре.")
        return
    
    await User.AddUser(id, username, fullname, chat_id)
    await message.answer(f"Привет, {message.from_user.full_name}! Вы добавлены в игру.")

# Обработчик команды /help
@dp.message(Command("help"))
async def command_start_handler(message: types.Message):
    await message.answer(help_text)


# Обработчик команды /gtop
@dp.message(Command("gtop"))
async def command_start_handler(message: types.Message):
    global GTop_text
    users = await User.GTopUsers()
    for i, user in enumerate(users, 1):
        GTop_text += f"{i}) {user.fullname} {user.lvl}\n"
    await message.answer(GTop_text)

# Обработчик команды /profile
@dp.message(Command("profile"))
async def command_start_handler(message: types.Message):
    global Profile_text
    id = message.from_user.id
    # fullname = message.from_user.full_name
    if not await User.UserExist(id):
        await message.answer(f"Вы не в игре.\nПропишите /start чтобы войти в игру")
        return
    
    user = await User.GetUser(id)
    cars_rarity = await Car.GetCarsRarity()
    user_cars_rarity = await User.GetUserCarsRarity(user)
    # print(user_cars_rarity)
    common = [user_cars_rarity[0]["count"], cars_rarity[0]["count"]]
    rare = [user_cars_rarity[1]["count"] , cars_rarity[1]["count"]]
    super_rare = [user_cars_rarity[2]["count"] , cars_rarity[2]["count"]]
    epic = [user_cars_rarity[3]["count"] , cars_rarity[3]["count"]]
    mythic = [user_cars_rarity[4]["count"] , cars_rarity[4]["count"]]
    legendary = [user_cars_rarity[5]["count"] , cars_rarity[5]["count"]]

    Profile_text = Profile_text_template.format(
        user.fullname, 
        user.cars_count, 
        common[1]+rare[1]+super_rare[1]+epic[1]+mythic[1]+legendary[1], 
        user.lvl, 
        common[0], common[1], 
        rare[0], rare[1], 
        super_rare[0], super_rare[1],
        epic[0], epic[1],
        mythic[0], mythic[1], 
        legendary[0], legendary[1], 
        user.pts
    )
    await message.answer(Profile_text, parse_mode=ParseMode.MARKDOWN_V2)


# Обработчик команды /cars
@dp.message(Command("cars"))
async def command_start_handler(message: types.Message):
    global Cars_text_template
    id = message.from_user.id
    if not await User.UserExist(id):
        await message.answer(f"Вы не в игре.\nПропишите /start чтобы войти в игру")
        return
    user = await User.GetUser(id)
    time_left, ok = await User.CheckTimeCar(user)
    if not ok:
        await message.answer(f"Попробуйте через {divmod(time_left, 60)[0]} минут {divmod(time_left, 60)[1]} секунд")
        return
    
    car = await Car.GetRandomCar()
    user_car, created = await user.AddOrAppendCar(car)

    new = "Новая" if created else "Повторка" 
    print(new, created)
    Cars_text = Cars_text_template.format(car.brand.replace('-', '\-'), CarRarity.get_name(car.rarity), 0, 1488, new, 69)
    await message.answer(Cars_text, parse_mode=ParseMode.MARKDOWN_V2)
    await User.UpdateTimeCar(user)



# функция запуска бота и инита базы данных
async def main():
    try:
        await init()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await Tortoise.close_connections()
        print('database connection close')

if __name__ == "__main__":
    try:
        print('Бот запущен')
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")