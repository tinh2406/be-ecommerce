import uuid

from django.db.models import CharField, UUIDField

from core.models import BaseTimeModel


class ProductsMapper(BaseTimeModel):

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)

    data = CharField(max_length=255)
    primary_key = CharField(max_length=255)

    total = CharField(max_length=255)
    total_page = CharField(max_length=255)
    take = CharField(max_length=255)
    page = CharField(max_length=255)

    cache_key_fields = ["id"]
    key = "products_mapper_"

    class Meta:
        ordering = ["-created_at"]
        db_table = "products_mappers"
        app_label = "crawlers"
