from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ProductAttribute(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    product = ForeignKey(
        "products.Product", on_delete=CASCADE, related_name="attributes"
    )
    name = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "product_attributes"
