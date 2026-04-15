from tortoise import models, fields


class User(models.Model):
    id = fields.BigIntField(pk=True, generated=False)
    chat_id = fields.BigIntField()
    username = fields.CharField(max_length=100)
    fullname = fields.CharField(max_length=100)
    cars_count = fields.IntField(default=0)
    pts = fields.DecimalField(decimal_places=2, max_digits=12, default=0.0)
    lvl = fields.IntField(default=1)

    def __str__(self):
        return f"<User: {self.id}>"
    

class Car(models.Model):
    id = fields.IntField(pk=True)
    brand = fields.CharField(max_length=200)
    # добавить редкость ну кароче ты понял сделай все круто

    def __str__(self):
        return f"<CAR: {self.id}|{self.brand}>"


class UserCar(models.Model):
    id = fields.IntField(pk=True)
    count = fields.IntField(default=1)
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
        return f"<UserCar: {self.user_id} owns {self.count} of {self.car_id}>"
    
    class Meta:
        # Опционально: запретить дубликаты (один и тот же юзер + та же машина)
        unique_together = (("user", "car"),)
    