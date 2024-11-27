import uuid

from django.db.models import PROTECT, ForeignKey, Manager, Model, UUIDField


class UserLikeProduct(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user = ForeignKey("users.User", on_delete=PROTECT, related_name="like_products")
    product = ForeignKey(
        "products.Product", on_delete=PROTECT, related_name="like_users"
    )

    objects = Manager()

    class Meta:
        db_table = "user_like_products"
