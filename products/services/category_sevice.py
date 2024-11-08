from typing import Union

from core.services import BaseService
from products.models import Category
from products.utils.simple_category_serializer import SimpleCategorySerializer

from .es_category_service import ESCategoryService


class CategoryService(BaseService):

    manager = Category.objects
    es_service = ESCategoryService

    @classmethod
    def create(cls, validated, **kwargs) -> Category:
        name = validated.get("name")
        parent_id = validated.get("parent_id")
        source_id = validated.get("source_id")

        category = Category.objects.create(
            name=name, source_id=source_id, parent_id=parent_id
        )

        serializer = SimpleCategorySerializer(category)
        ESCategoryService.index.delay(serializer.data)
        return category

    @classmethod
    def update(
        cls, instance: Category, validated: dict, partial=False, **kwargs
    ) -> Union[Category, None]:
        if partial:

            instance.name = validated.get("name", instance.name)
            instance.parent_id = validated.get("parent_id")

        else:
            instance.name = validated.get("name")
            instance.parent_id = validated.get("parent_id")

        instance.save()
        serializer = SimpleCategorySerializer(instance)
        ESCategoryService.index.delay(serializer.data)
        return instance
