from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.constants import Roles
from users.serializers import AddressSerializer
from users.services.address_service import AddressService


class AddressViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = AddressService.create(user_id=user.id, **serializer.validated_data)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        if user.role in [Roles.ADMIN, Roles.STAFF]:
            address = AddressService.get(pk)
        else:
            address = AddressService.get(pk, user_id=user.id)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        user = request.user

        if user.role in [Roles.ADMIN, Roles.STAFF]:
            queryset = AddressService.list(**request.query_params)
        else:
            queryset = AddressService.list(user_id=user.id)
        serializer = AddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")
        partial = kwargs.pop("partial", False)
        address = AddressService.get(pk, user_id=user.id)
        serializer = AddressSerializer(address, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        address = AddressService.update(
            address, validated=serializer.validated_data, partial=partial
        )
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        if AddressService.delete(pk, user_id=user.id):
            return Response({"message": "Address is deleted"})
        return Response({"message": "Address is not deleted"})

    @action(methods=["GET"], detail=False)
    def cities(self, request, *args, **kwargs):
        return Response(AddressService.list_cities(**request.query_params))

    @action(methods=["GET"], detail=False)
    def districts(self, request, *args, **kwargs):
        city = request.query_params.get("city")
        if not city:
            return Response({"message": "City is required"}, status=400)
        return Response(AddressService.list_districts(city, **request.query_params))

    @action(methods=["GET"], detail=False)
    def wards(self, request, *args, **kwargs):
        district = request.query_params.get("district")
        if not district:
            return Response({"message": "District is required"}, status=400)
        return Response(AddressService.list_wards(district, **request.query_params))
