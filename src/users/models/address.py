import uuid

from django.db.models import CASCADE, CharField, ForeignKey, UUIDField

from core.models import BaseCacheModel


class Address(BaseCacheModel):

    id = UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = ForeignKey("users.User", on_delete=CASCADE, related_name="addresses")

    city = CharField(max_length=5)
    district = CharField(max_length=5)
    ward = CharField(max_length=5)

    detail = CharField(max_length=255)

    key: str = "address_"
    cache_key_fields = ["id"]
    cache_time = 7 * 24 * 60 * 60

    class Meta:
        db_table = "addresses"
