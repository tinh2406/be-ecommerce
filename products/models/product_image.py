from uuid import uuid4

from django.db.models import CASCADE, CharField, ForeignKey, Manager, Model, UUIDField


class ProductImage(Model):
    id = UUIDField(primary_key=True, editable=False, default=uuid4)
    product = ForeignKey("products.Product", on_delete=CASCADE, related_name="images")
    url = CharField(max_length=255)

    objects = Manager()

    class Meta:
        db_table = "product_images"
