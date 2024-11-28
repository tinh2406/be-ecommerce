from core.domains import BaseDeleteDomain, BaseRetrieveDomain
from crawlers.services import ProductsMapperService


class ProductsMapperDomain(BaseRetrieveDomain, BaseDeleteDomain):

    main_service = ProductsMapperService

    @classmethod
    def create(cls, validated_mapper):
        mapper = ProductsMapperService.create(validated_mapper)
        return mapper.id

    @classmethod
    def update(cls, instance, validated_data):
        mapper = ProductsMapperService.update(instance, validated_data)
        return mapper.id

    @classmethod
    def search(cls, query_params):
        return ProductsMapperService.search(query_params)
