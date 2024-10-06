from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import PermissionDenied

from items.serializers import CategorySerializer
from items.services import CategoryService


class CategoryViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user or user.role != 1:
            raise PermissionDenied("You cannot do this action")

        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        category = CategoryService.get(pk)
        category_serializer = CategorySerializer(category)
        return Response(category_serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        if not user or user.role != 1:
            raise PermissionDenied("You cannot do this action")
        pk = kwargs.get('pk')
        partial = kwargs.get('partial', False)
        instance = CategoryService.get(pk)
        serializer = CategorySerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=partial)

        return Response(serializer.data)
