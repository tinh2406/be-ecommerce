from core.services import BaseRetrieveService, BaseDeleteService
from crawlers.domains import ProductsMapperDomain


class ProductsMapperService(BaseRetrieveService, BaseDeleteService):

    main_domain = ProductsMapperDomain

    @classmethod
    def create(cls, validated_mapper):
        mapper = ProductsMapperDomain.create(validated_mapper)
        return mapper.id

    @classmethod
    def update(cls, instance, validated_data):
        mapper = ProductsMapperDomain.update(instance, validated_data)
        return mapper.id

    @classmethod
    def search(cls, query_params):
        return ProductsMapperDomain.search(query_params)
