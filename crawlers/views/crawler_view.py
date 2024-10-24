from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.serializers import CrawlerSerializer
from crawlers.services import CrawlerService


class CrawlerViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = CrawlerSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        crawler_id = data.save()
        return Response({"data": crawler_id})

    def retrieve(self, request, *args, **kwargs):
        instance = CrawlerService.get(kwargs.get("pk"))
        data = CrawlerSerializer(instance).data
        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = CrawlerService.get(kwargs.get("pk"))
        data = CrawlerSerializer(instance, data=request.data)
        data.is_valid(raise_exception=True)

        crawler_id = data.save()
        return Response({"data": crawler_id})

    @action(detail=True, methods=["post"])
    def activate(self, request, *args, **kwargs):
        CrawlerService.activate_task(kwargs.get("pk"))
        return Response({"data": True})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, *args, **kwargs):
        CrawlerService.deactivate_task(kwargs.get("pk"))
        return Response({"data": True})

    def destroy(self, request, *args, **kwargs):
        CrawlerService.delete(kwargs.get("pk"))
        return Response({"data": True})
