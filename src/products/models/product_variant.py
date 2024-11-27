from uuid import uuid4

from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    Model,
    UUIDField,
)


class ProductVariant(Model):
    id = UUIDField(primary_key=True, default=uuid4)
    price = DecimalField(max_digits=10, decimal_places=2)
    hot_price = DecimalField(max_digits=10, decimal_places=2, null=True)
    image = CharField(max_length=255, null=True)
    product = ForeignKey("products.Product", on_delete=CASCADE, related_name="variants")

    class Meta:
        db_table = "product_variants"
