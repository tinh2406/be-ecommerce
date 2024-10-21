from crawlers.models import ProductMapper


class ProductMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductMapper:
        mapper = ProductMapper.objects.create(**validated)
        return mapper
