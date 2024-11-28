from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.domains import ProductsMapperDomain
from crawlers.serializers import (
    ProductsMapperSerializer,
    QueryProductMapperSerializer,
    SimpleProductsMapperSerializer,
)


class ProductsMapperViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = ProductsMapperSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = ProductsMapperDomain.create(data.validated_data)
        return Response({"data": mapper_id})

    def update(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ProductsMapperDomain.get(pk)

        data = ProductsMapperSerializer(instance, data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = ProductsMapperDomain.update(instance, data.validated_data)
        return Response({"data": mapper_id})

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ProductsMapperDomain.delete(pk)
        return Response({"data": True})

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ProductsMapperDomain.get(pk)

        return Response(ProductsMapperSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def restore(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        ProductsMapperDomain.restore(pk)
        return Response({"data": True})

    def list(self, request, *args, **kwargs):

        query_params = QueryProductMapperSerializer(data=request.query_params)
        query_params.is_valid(raise_exception=True)

        query_set, meta = ProductsMapperDomain.search(query_params.validated_data)
        mappers = SimpleProductsMapperSerializer(query_set, many=True).data

        return Response({"data": mappers, **meta})
