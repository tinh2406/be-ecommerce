from uuid import uuid4

from django.db.models import CASCADE, ForeignKey, Manager, Model, UUIDField


class ProductAttributeVariant(Model):

    id = UUIDField(primary_key=True, default=uuid4)
    product_variant = ForeignKey(
        "products.ProductVariant", on_delete=CASCADE, related_name="attributes"
    )
    product_attribute_value = ForeignKey(
        "products.ProductAttributeValue", on_delete=CASCADE, related_name="variants"
    )

    objects = Manager()

    class Meta:
        db_table = "product_attribute_variants"
