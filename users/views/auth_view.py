from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdatePasswordWithTokenSerializer,
)
from users.services import UserService


class AuthViewSet(ViewSet):

    permission_classes: list[object] = []
    authentication_classes: list[object] = []

    @action(methods=["POST"], detail=False)
    def register(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Register successfully"})

    @action(methods=["POST"], detail=False)
    def login(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = UserService.login(**serializer.validated_data)
        return Response(res)

    @action(methods=["POST"], detail=False)
    def request_token(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"message": "Email is required"}, status=400)

        UserService.request_token(email)
        return Response({"message": "Request verify token successfully"})

    @action(methods=["POST"], detail=False)
    def change_password(self, request):
        user = request.user

        serializer = UpdatePasswordWithTokenSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.save():
            return Response({"message": "Change password successfully"})

        return Response({"message": "Change password failed"}, status=400)
