from typing import Union

from rest_framework.exceptions import NotFound

from crawlers.models import ProductMapper


class ProductMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductMapper:
        mapper = ProductMapper.objects.create(**validated)
        return mapper

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
