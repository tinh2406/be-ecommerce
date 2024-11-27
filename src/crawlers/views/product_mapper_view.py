from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.serializers import (
    ProductMapperSerializer,
    QueryProductMapperSerializer,
    SimpleProductMapperSerializer,
)
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

    def destroy(self, request, *args, **kwargs):
        ProductMapperService.delete(kwargs.get("pk"))
        return Response({"data": True})

    def retrieve(self, request, *args, **kwargs):
        instance = ProductMapperService.get(kwargs.get("pk"))
        data = ProductMapperSerializer(instance).data
        return Response(data)

    @action(detail=True, methods=["post"])
    def restore(self, request, *args, **kwargs):
        ProductMapperService.restore(kwargs.get("pk"))
        return Response({"data": True})

    def list(self, request, *args, **kwargs):

        query_params = QueryProductMapperSerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)
        query_set, meta = ProductMapperService.search(query_params.validated_data)

        mappers = SimpleProductMapperSerializer(query_set, many=True).data

        return Response({"data": mappers, **meta})
