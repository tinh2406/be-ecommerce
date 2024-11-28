from core.services import BaseDeleteDomain, BaseRetrieveDomain
from crawlers.services import ProductMapperService


class ProductMapperDomain(BaseRetrieveDomain, BaseDeleteDomain):

    main_service = ProductMapperService

    @classmethod
    def create(cls, validated_mapper):
        mapper = ProductMapperService.create(validated_mapper)
        return mapper.id

    @classmethod
    def update(cls, instance, validated_data):
        mapper = ProductMapperService.update(instance, validated_data)
        return mapper.id

    @classmethod
    def search(cls, query_params):
        return ProductMapperService.search(query_params)
