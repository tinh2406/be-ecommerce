from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permission import Permission
from items.serializers import ItemSerializer
from items.services import ItemService


class ItemViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        instance = ItemService.get(pk)
        return Response(instance)

    def update(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        instance = ItemService.get(pk, use_cache=False)
        serializer = ItemSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        Permission.check_admin_permission(request)

        pk = kwargs.get("pk")
        ItemService.delete(pk)
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        Permission.check_admin_permission(request)

        ItemService.restore(pk)
        return Response(status=204)
