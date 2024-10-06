from rest_framework.exceptions import NotFound
from django.utils import timezone
from items.models import Category


class CategoryService:

    @classmethod
    def create(cls, validated, **kwargs)->Category:
        name = validated.get('name')
        parent_id = validated.get('parent_id')

        category = Category.objects.create(name=name,parent_id=parent_id)
        return category

    @classmethod
    def get(cls, pk, raise_exception=True, allow_deleted=False, use_cache=True)->Category|None:
        try:
            category = Category.cache_load(id=pk) if use_cache else Category.objects.get(pk=pk)

            if not allow_deleted and category.deleted_at:
                raise NotFound("Category not found")

            return category
        except Exception as e:
            if raise_exception:
                raise NotFound("Category not found")
            return None




