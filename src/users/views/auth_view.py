from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from users.domains import AuthDomain
from users.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdatePasswordWithTokenSerializer,
)
from users.serializers.user_serializer import RequestTokenSerializer


class AuthViewSet(ViewSet):

    permission_classes: list[object] = []
    authentication_classes: list[object] = []

    @action(methods=["POST"], detail=False)
    def register(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthDomain.register(serializer.validated_data)
        return Response({"message": "Register successfully"})

    @action(methods=["POST"], detail=False)
    def login(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login_data = AuthDomain.login(**serializer.validated_data)
        return Response(login_data)

    @action(methods=["POST"], detail=False)
    def request_token(self, request):
        serializer = RequestTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthDomain.request_token(**serializer.validated_data)
        return Response({"message": "Request verify token successfully"})

    @action(methods=["POST"], detail=False)
    def change_password(self, request):
        serializer = UpdatePasswordWithTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if AuthDomain.reset_password_by_token(**serializer.validated_data):
            return Response({"message": "Change password successfully"})
        return Response({"message": "Change password failed"}, status=400)
