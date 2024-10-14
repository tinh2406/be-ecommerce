from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permission import Permission
from products.serializers import ProductSerializer
from products.serializers.product_serializer import QueryProductSerializer
from products.services import ProductService
from products.services.es_product_service import ESProductService


class ProductViewSet(ModelViewSet):

    # permission_classes = []
    # authentication_classes = []

    def create(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ProductService.get(pk)
        serializer = ProductSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        instance = ProductService.get(pk, use_cache=False)
        serializer = ProductSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        ProductService.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        Permission.check_admin_permission(request)

        ProductService.restore(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        query = QueryProductSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        categories = ESProductService.search(query.data)
        return Response(categories)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        user = request.user
        res = QueryProductSerializer.like(pk, user_id=user.id)
        return Response(res)

    @action(detail=True, methods=["delete"])
    def unlike(self, request, pk=None):
        user = request.user
        res = QueryProductSerializer.unlike(pk, user_id=user.id)
        return Response(res)
