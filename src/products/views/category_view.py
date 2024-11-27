from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permission import Permission
from products.domains import CategoryDomain
from products.serializers import CategorySerializer, QueryCategorySerializer


class CategoryViewSet(ModelViewSet):

    permission_classes: list[object] = []

    def create(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = CategoryDomain.create(serializer.validated_data)

        return Response(
            CategorySerializer(category).data, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        category = CategoryDomain.get(pk)
        category_serializer = CategorySerializer(category)
        return Response(category_serializer.data)

    def update(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        category = CategoryDomain.get(pk)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)

        CategoryDomain.update(category, serializer.validated_data)
        return Response(CategorySerializer(category).data)

    def destroy(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        CategoryDomain.delete(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        Permission.check_admin_permission(request)

        CategoryDomain.restore(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        query = QueryCategorySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        categories = CategoryDomain.search_categories(query.data)
        return Response(categories)
