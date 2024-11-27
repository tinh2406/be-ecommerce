from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.constants import Roles
from users.domains import AddressDomain
from users.serializers import AddressSerializer


class AddressViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address = AddressDomain.create(user_id=user.id, **serializer.validated_data)
        return Response(AddressSerializer(address).data)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        if user.role in [Roles.ADMIN, Roles.STAFF]:
            address = AddressDomain.get(pk)
        else:
            address = AddressDomain.get(pk, user_id=user.id)
        return Response(AddressSerializer(address).data)

    def list(self, request, *args, **kwargs):
        user = request.user

        if user.role in [Roles.ADMIN, Roles.STAFF]:
            queryset = AddressDomain.list(**request.query_params)
        else:
            queryset = AddressDomain.list(user_id=user.id)

        return Response(AddressSerializer(queryset, many=True).data)

    def update(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        address = AddressDomain.get(pk, user_id=user.id)
        serializer = AddressSerializer(address, data=request.data)
        serializer.is_valid(raise_exception=True)
        AddressDomain.update(address, update_data=serializer.validated_data)

        return Response({"message": "Address is updated"})

    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = kwargs.get("pk")

        if AddressDomain.delete(pk, user_id=user.id):
            return Response({"message": "Address is deleted"})
        return Response({"message": "Address is not deleted"})

    @action(methods=["GET"], detail=False)
    def cities(self, request, *args, **kwargs):
        return Response(AddressDomain.list_cities(**request.query_params))

    @action(methods=["GET"], detail=False)
    def districts(self, request, *args, **kwargs):
        city = request.query_params.get("city")
        if not city:
            return Response({"message": "City is required"}, status=400)

        return Response(AddressDomain.list_districts(city, **request.query_params))

    @action(methods=["GET"], detail=False)
    def wards(self, request, *args, **kwargs):
        district = request.query_params.get("district")
        if not district:
            return Response({"message": "District is required"}, status=400)
        return Response(AddressDomain.list_wards(district, **request.query_params))
