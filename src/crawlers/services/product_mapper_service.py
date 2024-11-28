from core.services import BaseDeleteService, BaseRetrieveService
from crawlers.domains import ProductMapperDomain


class ProductMapperService(BaseDeleteService, BaseRetrieveService):

    main_domain = ProductMapperDomain

    @classmethod
    def create(cls, validated_mapper):
        mapper = ProductMapperDomain.create(validated_mapper)
        return mapper.id

    @classmethod
    def update(cls, instance, validated_data):
        mapper = ProductMapperDomain.update(instance, validated_data)
        return mapper.id

    @classmethod
    def search(cls, query_params):
        return ProductMapperDomain.search(query_params)
