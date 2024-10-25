from typing import Union

from celery import shared_task
from django.utils import timezone
from rest_framework.exceptions import NotFound

from products.models import Category, Product, UserLikeProduct
from products.serializers.simple_product_serializer import SimpleProductSerializer
from products.services.category_sevice import CategoryService

from .es_product_service import ESProductService
from .product_attribute_service import ProductAttributeService
from .product_image_service import ProductImageService


class ProductService:

    @staticmethod
    def create_product(
        validated: dict,
    ):
        name = validated.get("name")
        price = validated.get("price")
        thumbnail = validated.get("thumbnail")
        category_id = validated.get("category_id")
        description = validated.get("description")
        hot_price = validated.get("hot_price")

        images = validated.get("images", None)
        attributes = validated.get("attributes", None)
        variants = validated.get("variants", None)
        source_id = validated.get("product_id", None)

        product = Product.objects.create(
            name=name,
            description=description,
            thumbnail=thumbnail,
            price=price,
            category_id=category_id,
            hot_price=hot_price,
            source_id=source_id,
        )
        if images:
            ProductImageService.create_multiple(images, product.id)
        if attributes and variants:
            ProductAttributeService.create_multiple(attributes, variants, product.id)

        serializer = SimpleProductSerializer(product)
        ESProductService.index.delay(serializer.data)

        return product

    @staticmethod
    @shared_task
    def create_product_in_background(validated: dict, **kwargs) -> bool:
        if validated.get("product_id"):
            instance = Product.objects.filter(
                source_id=validated.get("product_id")
            ).first()
            if instance:
                return False

        try:
            category = Category.objects.filter(
                source_id=validated.get("category_id")
            ).first()
        except Category.DoesNotExist:
            category = None
        if not category:
            category = CategoryService.create(
                {
                    "name": validated.get("category_name"),
                    "source_id": validated.get("category_id"),
                }
            )

        validated["category_id"] = category.id
        ProductService.create_product(validated)
        return True

    @classmethod
    def get(
        cls, pk, raise_exception=True, allow_deleted=False, **kwargs
    ) -> Union[Product, None]:
        try:
            product = Product.objects.get(
                id=pk,
                related_fields=[
                    "images",
                    "category",
                    "attributes__values",
                    "variants__attributes__product_attribute_value__attribute",
                ],
            )
            if not allow_deleted and product.deleted_at:
                raise NotFound("Product not found")
            return product
        except Exception:
            if raise_exception:
                raise NotFound("Product not found")
            return None

    @classmethod
    def update(
        cls, instance: Product, validated: dict, **kwargs
    ) -> Union[Product, None]:

        instance.name = validated.get("name")
        instance.price = validated.get("price")
        instance.thumbnail = validated.get("thumbnail")
        instance.category_id = validated.get("category_id")
        instance.description = validated.get("description")
        instance.hot_price = validated.get("hot_price")

        images = validated.get("images", None)
        attributes = validated.get("attributes", None)
        variants = validated.get("variants", None)

        if images:
            ProductImageService.delete_multiple(instance.id)
            ProductImageService.create_multiple(images, instance.id)
        if attributes and variants:
            ProductAttributeService.delete_multiple(instance.id)
            ProductAttributeService.create_multiple(attributes, variants, instance.id)

        instance.save()
        serializer = SimpleProductSerializer(instance)
        ESProductService.index.delay(serializer.data)
        return instance

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk, use_cache=False)

        instance.deleted_at = timezone.now()
        instance.save()

        ESProductService.delete.delay(str(pk))
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.get(pk, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        ESProductService.restore.delay(str(pk))
        return True

    @classmethod
    def like(cls, pk, user_id):
        cls.get(pk)
        UserLikeProduct.objects.create(user_id=user_id, product_id=pk)
        return True

    @classmethod
    def unlike(cls, pk, user_id):
        UserLikeProduct.objects.filter(user_id=user_id, product_id=pk).delete()
        return True
