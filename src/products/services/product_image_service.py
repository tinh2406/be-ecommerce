from typing import List

from products.models import ProductImage


class ProductImageService:

    @classmethod
    def create(cls, url, product_id, **kwargs) -> ProductImage:
        product_image = ProductImage.objects.create(url=url, product_id=product_id)
        return product_image

    @classmethod
    def bulk_create(
        cls, validated_product: dict, product_id: str, **kwargs
    ) -> List[ProductImage]:
        images: list | None = validated_product.get("images", None)
        if not images:
            return []

        product_images = [
            ProductImage(url=image, product_id=product_id) for image in images
        ]
        ProductImage.objects.bulk_create(product_images)
        return product_images

    @classmethod
    def delete_multiple(cls, product_id):
        ProductImage.objects.filter(product_id=product_id).only("id").delete()
