from typing import Union

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
