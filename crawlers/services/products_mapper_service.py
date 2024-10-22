from typing import Union

from django.utils import timezone
from rest_framework.exceptions import NotFound

from crawlers.models import ProductsMapper


class ProductsMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductsMapper:
        mapper = ProductsMapper.objects.create(**validated)
        return mapper

    @classmethod
    def update(cls, instance: ProductsMapper, validated: dict) -> ProductsMapper:

        for key, value in validated.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    @classmethod
    def get(
        cls, pk: int, raise_exception: bool = True, allow_deleted: bool = False
    ) -> Union["ProductsMapper", None]:
        try:
            mapper = ProductsMapper.objects.get(id=pk)
            if not allow_deleted and mapper.deleted_at:
                raise NotFound("Mapper not found")
            return mapper
        except ProductsMapper.DoesNotExist:
            if raise_exception:
                raise NotFound("Mapper not found")
            return None

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.deleted_at = timezone.now()
        instance.save()
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.get(pk, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        return True
