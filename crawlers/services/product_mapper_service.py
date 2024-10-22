from typing import Union

from django.utils import timezone
from rest_framework.exceptions import NotFound

from crawlers.models import ProductMapper


class ProductMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductMapper:
        mapper = ProductMapper.objects.create(**validated)
        return mapper

    @classmethod
    def update(cls, instance: ProductMapper, validated: dict) -> ProductMapper:

        for key, value in validated.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    @classmethod
    def get(
        cls, pk: int, raise_exception: bool = True, allow_deleted: bool = False
    ) -> Union["ProductMapper", None]:
        try:
            mapper = ProductMapper.objects.get(id=pk)
            if not allow_deleted and mapper.deleted_at:
                raise NotFound("Mapper not found")
            return mapper
        except ProductMapper.DoesNotExist:
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
