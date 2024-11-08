from typing import Union

from rest_framework.exceptions import NotFound

from core.services import BaseService
from products.models import Product, UserLikeProduct
from products.serializers.simple_product_serializer import SimpleProductSerializer

from .es_product_service import ESProductService
from .product_attribute_service import ProductAttributeService
from .product_image_service import ProductImageService


class ProductService(BaseService):

    manager = Product.objects
    es_service = ESProductService

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

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs) -> Union[Product, None]:
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
            if product:
                return product
        except Exception:
            pass
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
    def like(cls, pk, user_id):
        cls.get(pk)
        UserLikeProduct.objects.create(user_id=user_id, product_id=pk)
        return True

    @classmethod
    def unlike(cls, pk, user_id):
        UserLikeProduct.objects.filter(user_id=user_id, product_id=pk).delete()
        return True
