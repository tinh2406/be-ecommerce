from core.domains import BaseDeleteDomain, BaseRetrieveDomain
from products.models import Product
from products.serializers import ProductSerializer
from products.services import (
    CategoryService,
    ESProductService,
    ProductAttributeService,
    ProductImageService,
    ProductService,
)


class ProductDomain(BaseRetrieveDomain, BaseDeleteDomain):

    @classmethod
    def create_product(cls, validated_product: dict) -> Product:

        CategoryService.get(validated_product["category_id"], raise_exception=True)

        product = ProductService.create_product(validated_product)
        ProductImageService.bulk_create(validated_product, product.id)
        ProductAttributeService.bulk_create(validated_product, product.id)

        ESProductService.index.delay(ProductSerializer(product).data)
        return product

    @classmethod
    def update(cls, product: Product, validated_product: dict) -> Product:

        CategoryService.get(validated_product["category_id"], raise_exception=True)

        ProductImageService.delete_multiple(product.id)
        ProductImageService.bulk_create(validated_product, product.id)
        ProductAttributeService.delete_multiple(product.id)
        ProductAttributeService.bulk_create(validated_product, product.id)

        product = ProductService.update(product, validated_product)

        ESProductService.index.delay(ProductSerializer(product).data)
        return product

    @classmethod
    def on_delete_success(cls, pk: str):
        ESProductService.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk: str):
        ESProductService.restore.delay(pk)

    @classmethod
    def search_products(cls, query: dict, user_id: str):

        response = ESProductService.search(query)

        products = response.pop("data")
        new_products = []
        for product in products:
            is_like = False
            if user_id:
                is_like = ProductService.check_is_like(product.id, user_id)
            new_products.append({**product, "is_like": is_like})
        response["data"] = new_products
        return response

    @classmethod
    def get_by_ids(cls, product_ids: list, user_id: str):

        products = ESProductService.get_list_by_ids(product_ids)
        new_products = []
        for product in products:
            is_like = False
            if user_id:
                is_like = ProductService.check_is_like(product.id, user_id)
            new_products.append({**product, "is_like": is_like})

        return new_products

    @classmethod
    def get_wish_list(cls, user_id: str):
        product_ids = ProductService.get_wish_list(user_id)
        products = ESProductService.get_list_by_ids(product_ids)
        return products

    @classmethod
    def like(cls, pk: str, user_id: str):
        ProductService.like(pk, user_id)
        return True

    @classmethod
    def unlike(cls, pk: str, user_id: str):
        ProductService.unlike(pk, user_id)
        return True
