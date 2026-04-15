import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv
from tortoise import Tortoise

from database import init, AddUser, UserExist, GTopUsers, GetUser


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

GTop_text = """
Глобальный топ:
""" 

Profile_text = """
{}
··············
{} из {} машин
{} уровень
··············
Обычных: {} из {}
Редких: {} из {}
Сверхредких: {} из {}
Эпических: {} из {}
Мифических: {} из {}
Легендарных: {} из {}
··············
{} pts
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

    if await UserExist(id):
        await message.answer(f"Привет, {fullname}! Вы уже в игре.")
        return
    
    await AddUser(id, username, fullname, chat_id)
    await message.answer(f"Привет, {message.from_user.full_name}! Вы добавлены в игру.")

# Обработчик команды /help
@dp.message(Command("help"))
async def command_start_handler(message: types.Message):
    await message.answer(help_text)


# Обработчик команды /gtop
@dp.message(Command("gtop"))
async def command_start_handler(message: types.Message):
    global GTop_text
    users = await GTopUsers()
    for i, user in enumerate(users, 1):
        GTop_text += f"{i}) {user.fullname} {user.lvl}\n"
    await message.answer(GTop_text)

# Обработчик команды /profile
@dp.message(Command("profile"))
async def command_start_handler(message: types.Message):
    global Profile_text
    id = message.from_user.id
    # fullname = message.from_user.full_name
    if not UserExist(id):
        await message.answer(f"Вы не в игре.\nПропишите /start чтобы войти в игру")
        return
    
    user = await GetUser(id)
    Profile_text.format(user.fullname, user.cars_count, 1, user.lvl, 2,3,4,5,6,7,8,9,10,11,12,13, user.pts)

    await message.answer(Profile_text)


# @dp.message(Command("test"))
# async def command_start_handler(message: types.Message):
#     user = await UserInfo(1559141063)
#     user_cars = [uc.car.brand for uc in user.user_cars]
#     await message.answer(f"{user_cars}")



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