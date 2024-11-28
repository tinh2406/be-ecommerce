from core.services import BaseDeleteService, BaseRetrieveService
from products.domains import (
    CategoryDomain,
    ESProductDomain,
    ProductAttributeDomain,
    ProductDomain,
    ProductImageDomain,
)
from products.models import Product
from products.serializers import ProductSerializer


class ProductService(BaseDeleteService, BaseRetrieveService):

    main_domain = ProductDomain

    @classmethod
    def create_product(cls, validated_product: dict) -> Product:

        CategoryDomain.get(validated_product["category_id"], raise_exception=True)

        product = ProductDomain.create_product(validated_product)
        ProductImageDomain.bulk_create(validated_product, product.id)
        ProductAttributeDomain.bulk_create(validated_product, product.id)

        ESProductDomain.index.delay(ProductSerializer(product).data)
        return product

    @classmethod
    def update(cls, product: Product, validated_product: dict) -> Product:

        CategoryDomain.get(validated_product["category_id"], raise_exception=True)

        ProductImageDomain.delete_multiple(product.id)
        ProductImageDomain.bulk_create(validated_product, product.id)
        ProductAttributeDomain.delete_multiple(product.id)
        ProductAttributeDomain.bulk_create(validated_product, product.id)

        product = ProductDomain.update(product, validated_product)

        ESProductDomain.index.delay(ProductSerializer(product).data)
        return product

    @classmethod
    def on_delete_success(cls, pk: str):
        ESProductDomain.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk: str):
        ESProductDomain.restore.delay(pk)

    @classmethod
    def search_products(cls, query: dict, user_id: str):

        response = ESProductDomain.search(query)

        products = response.pop("data")
        new_products = []
        for product in products:
            is_like = False
            if user_id:
                is_like = ProductDomain.check_is_like(product.id, user_id)
            new_products.append({**product, "is_like": is_like})
        response["data"] = new_products
        return response

    @classmethod
    def get_by_ids(cls, product_ids: list, user_id: str):

        products = ESProductDomain.get_list_by_ids(product_ids)
        new_products = []
        for product in products:
            is_like = False
            if user_id:
                is_like = ProductDomain.check_is_like(product.id, user_id)
            new_products.append({**product, "is_like": is_like})

        return new_products

    @classmethod
    def get_wish_list(cls, user_id: str):
        product_ids = ProductDomain.get_wish_list(user_id)
        products = ESProductDomain.get_list_by_ids(product_ids)
        return products

    @classmethod
    def like(cls, pk: str, user_id: str):
        ProductDomain.like(pk, user_id)
        return True

    @classmethod
    def unlike(cls, pk: str, user_id: str):
        ProductDomain.unlike(pk, user_id)
        return True
