from rest_framework.exceptions import NotFound

from items.models import Item
from items.serializers.simple_item_serializer import SimpleItemSerializer

from .es_item_service import ESItemService
from .item_attribute_service import ItemAttributeService
from .item_image_service import ItemImageService


class ItemService:
    @classmethod
    def create(cls, validated: dict, **kwargs) -> Item:
        name = validated.get("name")
        price = validated.get("price")
        thumbnail = validated.get("thumbnail")
        category_id = validated.get("category_id")
        description = validated.get("description")
        hot_price = validated.get("hot_price")

        images = validated.get("images", None)
        attributes = validated.get("attributes", None)
        variants = validated.get("variants", None)

        item = Item.objects.create(
            name=name,
            description=description,
            thumbnail=thumbnail,
            price=price,
            category_id=category_id,
            hot_price=hot_price,
        )
        if images:
            ItemImageService.create_multiple(images, item.id)
        if attributes and variants:
            ItemAttributeService.create_multiple(attributes, variants, item.id)

        serializer = SimpleItemSerializer(item)
        ESItemService.index.delay(serializer.data)

        return item

    @classmethod
    def get(
        cls, pk, raise_exception=True, allow_deleted=False, use_cache=True, **kwargs
    ) -> Item | None:
        try:
            if use_cache:
                item = Item.cache_load(id=pk)
                if not allow_deleted and item.get("deleted_at"):
                    raise NotFound("Item not found")
            else:
                item = Item.objects.get(pk=pk)
                if not allow_deleted and item.deleted_at:
                    raise NotFound("Item not found")
            return item
        except Exception:
            if raise_exception:
                raise NotFound("Item not found")
            return None

    @classmethod
    def update(cls, instance: Item, validated: dict, **kwargs) -> Item | None:

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
            ItemImageService.delete_multiple(instance.id)
            ItemImageService.create_multiple(images, instance.id)
        if attributes and variants:
            ItemAttributeService.delete_multiple(instance.id)
            ItemAttributeService.create_multiple(attributes, variants, instance.id)

        instance.save()
        serializer = SimpleItemSerializer(instance)
        ESItemService.index.delay(serializer.data)
        return instance
