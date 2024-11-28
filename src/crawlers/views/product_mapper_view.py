from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.domains import ProductMapperDomain
from crawlers.serializers import (
    ProductMapperSerializer,
    QueryProductMapperSerializer,
    SimpleProductMapperSerializer,
)


class ProductMapperViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        serializer = ProductMapperSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mapper_id = ProductMapperDomain.create(serializer.validated_data)
        return Response({"data": mapper_id})

    def update(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        instance = ProductMapperDomain.get(pk)
        data = ProductMapperSerializer(instance, data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = ProductMapperDomain.update(instance, data.validated_data)
        return Response({"data": mapper_id})

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        ProductMapperDomain.delete(pk)
        return Response({"data": True})

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ProductMapperDomain.get(pk)

        return Response(ProductMapperSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        ProductMapperDomain.restore(pk)
        return Response({"data": True})

    def list(self, request, *args, **kwargs):

        query_params = QueryProductMapperSerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)

        query_set, meta = ProductMapperDomain.search(query_params.validated_data)
        mappers = SimpleProductMapperSerializer(query_set, many=True).data

        return Response({"data": mappers, **meta})
