import asyncio
import random
from tortoise import Tortoise, run_async
from models import User, Car, UserCar

async def seed_data():
    # 1. Инициализация
    await Tortoise.init(db_url="sqlite://database.db", modules={"models": ['models']})
    await Tortoise.generate_schemas()

    # 2. Создаем 20 разных машин
    car_brands = [
        "BMW M5", "Tesla Model S", "Toyota Supra", "Audi RS6", "Porsche 911", 
        "Lada Vesta", "Nissan GT-R", "Ford Mustang", "Mercedes-AMG GT", "Hyundai Solaris",
        "Mazda RX-7", "Volkswagen Golf", "Dodge Challenger", "Chevrolet Camaro", "Subaru WRX",
        "Lexus LC500", "Honda NSX", "Ferrari F40", "Lamborghini Aventador", "Bugatti Chiron"
    ]
    
    cars_to_create = [Car(brand=brand) for brand in car_brands]
    await Car.bulk_create(cars_to_create, ignore_conflicts=True)
    all_cars = await Car.all()
    print(f"Загружено машин в справочник: {len(all_cars)}")

    # 3. Генерируем 50 пользователей
    users_to_create = []
    for i in range(50):
        fake_id = random.randint(100000000, 9999999999)
        users_to_create.append(User(
            id=fake_id,
            chat_id=fake_id, # Обычно в ЛС они совпадают
            username=f"player_{i}",
            fullname=f"Игрок №{i+1}",
            exp=random.uniform(0, 500),
            lvl=random.randint(1, 50)
        ))

    await User.bulk_create(users_to_create, ignore_conflicts=True)
    all_users = await User.all()
    print(f"Создано пользователей: {len(all_users)}")

    # 4. Раздаем машины (у каждого будет от 2 до 7 случайных машин)
    user_car_links = []
    for user in all_users:
        # Выбираем случайный набор машин
        count_of_models = random.randint(2, 7)
        assigned_cars = random.sample(all_cars, k=count_of_models)
        
        for car in assigned_cars:
            user_car_links.append(UserCar(
                user=user,
                car=car,
                count=random.randint(1, 3) # Количество экземпляров одной модели
            ))

    await UserCar.bulk_create(user_car_links, ignore_conflicts=True)
    print(f"Всего связей в гаражах создано: {len(user_car_links)}")

    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(seed_data())