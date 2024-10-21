from crawlers.models import ProductsMapper


class ProductsMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductsMapper:
        mapper = ProductsMapper.objects.create(**validated)
        return mapper
