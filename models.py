from tortoise.models import Model
import tortoise.fields


class User(Model):
    id = tortoise.fields.IntField(pk=True)
    name = tortoise.fields.CharField(max_length=150, default='Allax')
    phone = tortoise.fields.CharField(max_length=20, default='+1234567890')
    age = tortoise.fields.IntField()

    def __str__(self):
        return f"<User: {self.id}>"