from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.serializers import ProductMapperSerializer
from crawlers.services import ProductMapperService


class ProductMapperViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = ProductMapperSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = data.save()
        return Response({"data": mapper_id})

    def update(self, request, *args, **kwargs):
        instance = ProductMapperService.get(kwargs.get("pk"))
        data = ProductMapperSerializer(instance, data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = data.save()
        return Response({"data": mapper_id})

    def retrieve(self, request, *args, **kwargs):
        instance = ProductMapperService.get(kwargs.get("pk"))
        data = ProductMapperSerializer(instance).data
        return Response(data)
