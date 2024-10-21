from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.serializers import ProductsMapperSerializer
from crawlers.services import ProductsMapperService


class ProductsMapperViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = ProductsMapperSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = data.save()
        return Response({"data": mapper_id})

    def retrieve(self, request, *args, **kwargs):
        instance = ProductsMapperService.get(kwargs.get("pk"))
        data = ProductsMapperSerializer(instance).data
        return Response(data)
