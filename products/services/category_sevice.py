from typing import Union

from django.utils import timezone
from rest_framework.exceptions import NotFound

from products.models import Category
from products.utils.simple_category_serializer import SimpleCategorySerializer

from .es_category_service import ESCategoryService


class CategoryService:

    @classmethod
    def create(cls, validated, **kwargs) -> Category:
        name = validated.get("name")
        parent_id = validated.get("parent_id")

        category = Category.objects.create(name=name, parent_id=parent_id)

        serializer = SimpleCategorySerializer(category)
        ESCategoryService.index.delay(serializer.data)
        return category

    @classmethod
    def get(
        cls, pk, raise_exception=True, allow_deleted=False
    ) -> Union[Category, None]:
        try:
            category = Category.objects.get(id=pk)

            if not allow_deleted and category.deleted_at:
                raise NotFound("Category not found")

            return category
        except Exception:
            if raise_exception:
                raise NotFound("Category not found")
            return None

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

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.deleted_at = timezone.now()
        instance.save()
        ESCategoryService.delete.delay(str(pk))
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.get(pk, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        ESCategoryService.restore.delay(pk)
        return True
