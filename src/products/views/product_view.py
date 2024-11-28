from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permission import Permission
from products.serializers import ProductSerializer
from products.serializers.product_serializer import (
    QueryByListIds,
    QueryProductSerializer,
)
from products.services import ProductService


class ProductViewSet(ModelViewSet):

    permission_classes: list[object] = []

    def create(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.create_product(serializer.validated_data)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ProductService.get(pk)
        return Response(ProductSerializer(instance).data)

    def update(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        instance = ProductService.get(pk)
        serializer = ProductSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        product = ProductService.update(instance, serializer.validated_data)
        return Response(ProductSerializer(product).data)

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

        response = ProductService.search_products(
            query.validated_data, user_id=request.user.id
        )

        return Response(response)

    @action(detail=False, methods=["post"])
    def list_by_ids(self, request, *args, **kwargs):
        query = QueryByListIds(data=request.data)
        query.is_valid(raise_exception=True)

        products = ProductService.get_by_ids(
            query.validated_data["product_ids"], user_id=request.user.id
        )

        return Response(products)

    @action(detail=False, methods=["get"])
    def wish_list(self, request, *args, **kwargs):
        user = request.user
        products = ProductService.get_wish_list(user_id=user.id)
        return Response(products)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        user = request.user
        res = ProductService.like(pk, user_id=user.id)
        return Response(res)

    @action(detail=True, methods=["delete"])
    def unlike(self, request, pk=None):
        user = request.user
        res = ProductService.unlike(pk, user_id=user.id)
        return Response(res)
