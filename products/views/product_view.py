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
from products.services.es_product_service import ESProductService


class ProductViewSet(ModelViewSet):

    permission_classes: list[object] = []

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
        response = ESProductService.search(query.data)
        products = response.pop("data")
        new_products = []
        for product in products:
            is_like = False
            if request.user.id:
                is_like = ProductService.check_is_like(product.id, request.user.id)
            new_products.append({**product, "is_like": is_like})
        response["data"] = new_products
        return Response(response)

    @action(detail=False, methods=["post"])
    def list_by_ids(self, request, *args, **kwargs):
        query = QueryByListIds(data=request.data)
        query.is_valid(raise_exception=True)
        products = ESProductService.get_list_by_ids(query.data["product_ids"])
        new_products = []
        for product in products:
            is_like = False
            if request.user.id:
                is_like = ProductService.check_is_like(product.id, request.user.id)
            new_products.append({**product, "is_like": is_like})

        return Response(new_products)

    @action(detail=False, methods=["get"])
    def wish_list(self, request, *args, **kwargs):
        user = request.user
        product_ids = ProductService.get_wish_list(user.id)
        products = ESProductService.get_list_by_ids(product_ids)
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
