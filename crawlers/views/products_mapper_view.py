from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminPermission
from crawlers.serializers import ProductsMapperSerializer


class ProductsMapperViewSet(ModelViewSet):

    permission_classes = [IsAdminPermission]

    def create(self, request, *args, **kwargs):
        data = ProductsMapperSerializer(data=request.data)
        data.is_valid(raise_exception=True)

        mapper_id = data.save()
        return Response({"data": mapper_id})
