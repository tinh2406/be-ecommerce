from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ProductAttributeValue(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    attribute = ForeignKey(
        "products.ProductAttribute", on_delete=CASCADE, related_name="values"
    )
    value = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "product_attribute_values"
