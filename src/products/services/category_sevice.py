from typing import Union

from core.services import BaseService
from products.models import Category


class CategoryService(BaseService):

    manager = Category.objects

    @classmethod
    def create(cls, validated_category: dict, **kwargs) -> Category:
        name = validated_category.get("name")
        parent_id = validated_category.get("parent_id")
        source_id = validated_category.get("source_id")

        category = Category.objects.create(
            name=name, source_id=source_id, parent_id=parent_id
        )

        return category

    @classmethod
    def update(
        cls, instance: Category, validated: dict, **kwargs
    ) -> Union[Category, None]:

        instance.name = validated.get("name")
        instance.parent_id = validated.get("parent_id")

        instance.save()
        return instance
