from typing import List

from products.models import ProductImage


class ProductImageService:

    @classmethod
    def create(cls, url, product_id, **kwargs) -> ProductImage:
        product_image = ProductImage.objects.create(url=url, product_id=product_id)
        return product_image

    @classmethod
    def create_multiple(cls, images, product_id, **kwargs) -> List[ProductImage]:
        product_images = [
            ProductImage.objects.create(url=image, product_id=product_id)
            for image in images
        ]
        return product_images

    @classmethod
    def delete_multiple(cls, product_id):
        ProductImage.objects.filter(product_id=product_id).delete()
