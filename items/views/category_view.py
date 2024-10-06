from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import PermissionDenied

from items.serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user or user.role != 1:
            raise PermissionDenied("You cannot do this action")

        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)