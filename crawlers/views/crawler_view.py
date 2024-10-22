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
