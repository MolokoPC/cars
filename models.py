from tortoise import models, fields
from enum import IntEnum
from tortoise.functions import Count
from time import time
# from tortoise.expressions import Function
# from tortoise.expressions import RawSQL
from tortoise.contrib.sqlite.functions import Random
from tortoise.expressions import F

class CarRarity(IntEnum):
    COMMON = 1       # Обычный
    RARE = 2         # Редкий
    SUPER_RARE = 3   # Сверхредкий
    EPIC = 4         # Эпический
    MYTHIC = 5       # Мифический
    LEGENDARY = 6    # Легендарный

    @classmethod
    def get_name(cls, value: int) -> str:
        mapping = {
            cls.COMMON: "Обычный",
            cls.RARE: "Редкий",
            cls.SUPER_RARE: "Сверхредкий",
            cls.EPIC: "Эпический",
            cls.MYTHIC: "Мифический",
            cls.LEGENDARY: "Легендарный",
        }
        return mapping.get(value, "Неизвестно")


class User(models.Model):
    id = fields.BigIntField(pk=True, generated=False)
    chat_id = fields.BigIntField()
    username = fields.CharField(max_length=100)
    fullname = fields.CharField(max_length=100)
    cars_count = fields.IntField(default=0)
    pts = fields.DecimalField(decimal_places=2, max_digits=12, default=0.0)
    lvl = fields.IntField(default=1)
    last_use = fields.BigIntField(default=0)

    def __str__(self):
        return f"<User: {self.id}>"
    
    # --- Методы экземпляра (вызываются как user.method()) --- (разница просто в жопу мне чтото писть надоело о боже зачем кому я это пишу)
    # кароче хотел сказать что разница в то что self и user(экземпляр) != User(класс)

    async def GetUserCarsRarity(self):
        cars_rarity_raw = await UserCar.filter(user_id=self.id).annotate(count=Count("id")).group_by("car__rarity").values("car__rarity", "count")
        cars_rarity_raw = {res["rarity"]: res["count"] for res in cars_rarity_raw}
        
        cars_rarity = []
        for rarity in CarRarity:
            cars_rarity.append({
                "rarity": rarity,
                "count": cars_rarity_raw.get(rarity.value, 0)
            })
        return cars_rarity
    
    async def CheckTimeCar(self) -> list:
        now = int(time())
        cooldown = 0 #3600
        if now > (cooldown + self.last_use):
            return [0, True]
        return [cooldown+self.last_use-now, False]

    async def UpdateTimeCar(self) -> None:
        self.last_use = int(time())
        await self.save()

    async def AddOrAppendCar(self, car):
        user_car, created = await UserCar.get_or_create(
            user=self,
            car=car
        )
        if not created:
            # Использование F-выражения защищает от Race Condition
            user_car.car_count = F('car_count') + 1
            await user_car.save()

            # делает запрос
            await user_car.refresh_from_db(fields=['car_count'])

        self.cars_count = F('cars_count') + 1
        await self.save()

        return [user_car, created]


    # --- Методы класса (вызываются как User.method()) --- (тут чето можно изменить с userexist по getuser незн что но мне чешет руки (бомж))

    # проверка есть ли запись пользователя в базе 
    # работает вроде нормально но не знаю наверное нет (тут все работает через жопу)
    @classmethod
    async def UserExist(cls, id):
        exist = await cls.filter(id=id).exists()
        return exist
    
    # БЛЯТЬ ПЕРЕПИШИ ПОТОМ НАХУЙ ЭТИ ДВА НА ОДНО НО GET_OR_CREATE ПЖПЖПЖПЖПЖПЖПЖПЖПЖПЖПЖПЖП
    # добавляет нового пользователя
    # надо переделать на create or get или как там его 
    # для того чтобы выгладило красивее и меньше запросов 
    # но незн 50 на 50 думать надо
    @classmethod
    async def AddUser(cls, id, username, fullname, chat_id):
        user = await cls.create(id=id, username=username, fullname=fullname, chat_id=chat_id)
        return user
    
    # деф выдача пользователя
    @classmethod
    async def GetUser(cls, id):
        user = await cls.get_or_none(id=id)
        return user
    
    # простая первая версия
    # надо сделать с видами сортировки 
    # возможно добавить страницы типо первые 10 вторые 10 и так далее
    # можно вместить gtop и обыч top в одну функцию через передачу параметра и if 
    @classmethod
    async def GTopUsers(cls) -> list:
        users = await cls.all().order_by("-lvl").limit(10)
        return users

    
class Car(models.Model):
    id = fields.IntField(pk=True)
    brand = fields.CharField(max_length=200)
    # добавить редкость ну кароче ты понял сделай все круто
    rarity = fields.IntEnumField(CarRarity, default=CarRarity.COMMON)

    def __str__(self):
        return f"<CAR: {self.id}|{self.brand}>"
    # --- Методы класса (вызываются как Car.method()) ---

    # просто выдает все машины без ничего лишнего (без подгрузки связей)
    @classmethod
    async def GetCars(cls):
        cars = await cls.all()
        return cars
    
    # выдает список с словарями такого формата {"rarity": <CarRarity....>, "count": count}
    @classmethod
    async def GetCarsRarity(cls):
        cars_rarity = await cls.annotate(count=Count("id")).group_by("rarity").values("rarity", "count")
        return cars_rarity
    
    @classmethod
    async def GetRandomCar(cls):
        return await cls.annotate(random=Random()).order_by("random").first()
    


class UserCar(models.Model):
    id = fields.IntField(pk=True)
    car_count = fields.IntField(default=1)
    user = fields.ForeignKeyField(
        'models.User',
        related_name='user_cars',
        on_delete=fields.CASCADE
    )
    car = fields.ForeignKeyField(
        'models.Car',
        related_name='car_users',
        on_delete=fields.CASCADE
    )

    def __str__(self):
        return f"<UserCar object owns: {self.user_id} count: {self.car_count} car_id: {self.car_id}>"

    class Meta:
        # Опционально: запретить дубликаты (один и тот же юзер + та же машина)
        unique_together = (("user", "car"),)
    