from core.domains import BaseDeleteDomain, BaseRetrieveDomain
from crawlers.services import CrawlerService, RequestParamsService


class CrawlerDomain(BaseRetrieveDomain, BaseDeleteDomain):

    main_service = CrawlerService

    @classmethod
    def create(cls, validated_crawler):
        request_params_id = RequestParamsService.create(validated_crawler).id
        validated_crawler["request_params_id"] = request_params_id
        crawler = CrawlerService.create(validated_crawler)
        return crawler.id

    @classmethod
    def update(cls, crawler, validated_crawler):
        request_params_id = RequestParamsService.create(validated_crawler).id
        validated_crawler["request_params_id"] = request_params_id
        crawler = CrawlerService.update(crawler, validated_crawler)
        return crawler.id

    @classmethod
    def activate_task(cls, pk):
        CrawlerService.activate_task(pk)

    @classmethod
    def deactivate_task(cls, pk):
        CrawlerService.deactivate_task(pk)

    @classmethod
    def search(cls, query_params):
        return CrawlerService.search(query_params)
