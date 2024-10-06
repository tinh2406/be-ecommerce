import uuid
from uuid import uuid4

from django.db.models import PROTECT, CharField, IntegerField, ForeignKey, Manager, AutoField, UUIDField

from core.common import BaseTimeModel


class Category(BaseTimeModel):

    id = UUIDField(primary_key=True, auto_created=True, default=uuid4)
    name = CharField(max_length=255)

    parent = ForeignKey('items.Category',null=True, on_delete=PROTECT, related_name='childs')

    cache_fields = ['id']
    key = 'category_'

    objects = Manager()

    class Meta:
        db_table = 'categories'

