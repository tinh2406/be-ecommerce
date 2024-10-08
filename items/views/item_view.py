from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permission import Permission
from items.serializers import ItemSerializer


class ItemViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
