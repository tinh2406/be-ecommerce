import uuid

from django.db.models import CharField, JSONField, UUIDField

from core.models import BaseTimeModel


class ProductMapper(BaseTimeModel):

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)

    product_id = CharField(max_length=255)
    product_name = CharField(max_length=255)
    product_description = CharField(max_length=255)
    product_price = CharField(max_length=255)
    product_hot_price = CharField(max_length=255, null=True, blank=True)
    product_created_at = CharField(max_length=255, null=True, blank=True)
    product_updated_at = CharField(max_length=255, null=True, blank=True)
    product_deleted_at = CharField(max_length=255, null=True, blank=True)
    product_thumbnail = CharField(max_length=255, null=True, blank=True)
    product_category_id = CharField(max_length=255)
    product_category_name = CharField(max_length=255)
    product_images = CharField(max_length=255, null=True, blank=True)

    properties = JSONField(default=dict)

    cache_key_fields = ["id"]
    key = "product_mapper_"

    class Meta:
        ordering = ["-created_at"]
        db_table = "product_mappers"
        app_label = "crawlers"
