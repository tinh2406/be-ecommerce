from django.utils import timezone
from rest_framework.exceptions import NotFound

from items.models import Category

from .es_category_service import ESCategoryService


class CategoryService:

    @classmethod
    def create(cls, validated, **kwargs) -> Category:
        name = validated.get("name")
        parent_id = validated.get("parent_id")

        category = Category.objects.create(name=name, parent_id=parent_id)
        ESCategoryService.index(category)
        return category

    @classmethod
    def get(
        cls, pk, raise_exception=True, allow_deleted=False, use_cache=True
    ) -> Category | None:
        try:
            category = (
                Category.cache_load(id=pk) if use_cache else Category.objects.get(pk=pk)
            )

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
    ) -> Category | None:
        if partial:

            instance.name = validated.get("name", instance.name)
            instance.parent_id = validated.get("parent_id")

        else:
            instance.name = validated.get("name")
            instance.parent_id = validated.get("parent_id")

        instance.save()
        ESCategoryService.update(instance)
        return instance

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        try:
            instance.delete()
            ESCategoryService.delete(pk)
        except Exception:
            instance.deleted_at = timezone.now()
            instance.save()
            ESCategoryService.update(instance)
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.get(pk, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        ESCategoryService.update(instance)
        return True
