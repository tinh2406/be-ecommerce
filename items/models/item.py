import uuid

from django.db.models import UUIDField, CharField, TextField, ForeignKey, PROTECT, FloatField, Manager

from core.common import BaseTimeModel


class Item(BaseTimeModel):
    id = UUIDField(primary_key=True, default= uuid.uuid4)
    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKey('items.Category', on_delete=PROTECT, related_name='items')
    price = FloatField()
    hot_price = FloatField(null=True)
    image = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = 'items'


