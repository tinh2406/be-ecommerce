from core.services import BaseDeleteService, BaseRetrieveService
from crawlers.domains import CrawlerDomain, RequestParamsDomain


class CrawlerService(BaseDeleteService, BaseRetrieveService):

    main_domain = CrawlerDomain

    @classmethod
    def create(cls, validated_crawler):
        request_params_id = RequestParamsDomain.create(validated_crawler).id
        validated_crawler["request_params_id"] = request_params_id
        crawler = CrawlerDomain.create(validated_crawler)
        return crawler.id

    @classmethod
    def update(cls, crawler, validated_crawler):
        request_params_id = RequestParamsDomain.create(validated_crawler).id
        validated_crawler["request_params_id"] = request_params_id
        crawler = CrawlerDomain.update(crawler, validated_crawler)
        return crawler.id

    @classmethod
    def activate_task(cls, pk):
        CrawlerDomain.activate_task(pk)

    @classmethod
    def deactivate_task(cls, pk):
        CrawlerDomain.deactivate_task(pk)

    @classmethod
    def search(cls, query_params):
        return CrawlerDomain.search(query_params)
