from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.domains import CrawlerDomain
from crawlers.serializers import (
    CrawlerSerializer,
    DetailPeriodicTaskSerializer,
    PeriodicTaskSerializer,
    QueryCrawlerSerializer,
)


class CrawlerViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = CrawlerSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        crawler_id = CrawlerDomain.create(data.validated_data)
        return Response({"data": crawler_id})

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        crawler = CrawlerDomain.get(pk)

        return Response(DetailPeriodicTaskSerializer(crawler).data)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = CrawlerDomain.get(pk)

        data = CrawlerSerializer(instance, data=request.data)
        data.is_valid(raise_exception=True)

        crawler_id = CrawlerDomain.update(instance, data.validated_data)
        return Response({"data": crawler_id})

    @action(detail=True, methods=["post"])
    def activate(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        CrawlerDomain.activate_task(pk)
        return Response({"data": True})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        CrawlerDomain.deactivate_task(pk)
        return Response({"data": True})

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        CrawlerDomain.delete(pk)
        return Response({"data": True})

    def list(self, request, *args, **kwargs):

        query_params = QueryCrawlerSerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)

        query_set, meta = CrawlerDomain.search(query_params.validated_data)
        crawlers = PeriodicTaskSerializer(query_set, many=True).data

        return Response({"data": crawlers, **meta})
