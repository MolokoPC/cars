import asyncio
import random
from tortoise import Tortoise, run_async
from models import User, Car, UserCar, CarRarity

async def seed_data():
    # 1. Инициализация
    await Tortoise.init(
        db_url="sqlite://database.db", 
        modules={"models": ['models']}
    )
    await Tortoise.generate_schemas()

    # 2. Создаем 20 разных машин с рандомной редкостью
    car_brands = [
        "BMW M5", "Tesla Model S", "Toyota Supra", "Audi RS6", "Porsche 911", 
        "Lada Vesta", "Nissan GT-R", "Ford Mustang", "Mercedes-AMG GT", "Hyundai Solaris",
        "Mazda RX-7", "Volkswagen Golf", "Dodge Challenger", "Chevrolet Camaro", "Subaru WRX",
        "Lexus LC500", "Honda NSX", "Ferrari F40", "Lamborghini Aventador", "Bugatti Chiron"
    ]
    
    # Список всех редкостей из твоего Enum
    rarities = list(CarRarity)

    cars_to_create = []
    for brand in car_brands:
        cars_to_create.append(Car(
            brand=brand,
            # Случайная редкость для каждой машины
            rarity=random.choice(rarities)
        ))
    
    await Car.bulk_create(cars_to_create, ignore_conflicts=True)
    all_cars = await Car.all()
    print(f"✅ Загружено машин в справочник: {len(all_cars)}")

    # 3. Генерируем 50 пользователей
    users_to_create = []
    for i in range(50):
        fake_id = random.randint(100000000, 9999999999)
        users_to_create.append(User(
            id=fake_id,
            chat_id=fake_id,
            username=f"player_{i}",
            fullname=f"Игрок №{i+1}",
            pts=random.uniform(0, 5000), # В модели это pts вместо exp
            lvl=random.randint(1, 50),
            cars_count=0 # Обновим позже
        ))

    await User.bulk_create(users_to_create, ignore_conflicts=True)
    all_users = await User.all()
    print(f"✅ Создано пользователей: {len(all_users)}")

    # 4. Раздаем машины (у каждого будет от 2 до 7 случайных машин)
    user_car_links = []
    for user in all_users:
        count_of_models = random.randint(2, 7)
        # Берем случайные машины из базы
        assigned_cars = random.sample(all_cars, k=min(count_of_models, len(all_cars)))
        
        user_total_cars = 0
        for car in assigned_cars:
            car_count = random.randint(1, 3)
            user_total_cars += car_count
            
            user_car_links.append(UserCar(
                user=user,
                car=car,
                count=car_count
            ))
        
        # Обновляем счетчик машин у юзера
        user.cars_count = user_total_cars

    # Массово создаем связи в гаражах
    await UserCar.bulk_create(user_car_links, ignore_conflicts=True)
    
    # Массово обновляем поле cars_count у всех юзеров
    await User.bulk_update(all_users, fields=['cars_count'])
    
    print(f"✅ Всего записей в гаражах создано: {len(user_car_links)}")
    print("🚀 Сидирование данных завершено успешно!")

    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(seed_data())