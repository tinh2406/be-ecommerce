from typing import List

from items.models import ItemImage


class ItemImageService:

    @classmethod
    def create(cls, url, item_id, **kwargs) -> ItemImage:
        item_image = ItemImage.objects.create(url=url, item_id=item_id)
        return item_image

    @classmethod
    def create_multiple(cls, images, item_id, **kwargs) -> List[ItemImage]:
        item_images = [
            ItemImage.objects.create(url=image, item_id=item_id) for image in images
        ]
        return item_images
