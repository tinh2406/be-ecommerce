from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.constants import Roles
from users.serializers import (
    ChangeEmailSerializer,
    QueryUserSerializer,
    UpdatePasswordSerializer,
    UpdateRoleSerializer,
    UserSerializer,
)
from users.services import ESUserService, UserService


class UserViewSet(ModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if str(user.id) == kwargs.get("pk"):
            return self.me(request)
        if user.role not in (Roles.ADMIN, Roles.STAFF):
            return Response(
                {"message": "You do not have permission to access this user"},
                status=403,
            )

        instance = UserService.get(
            kwargs.get("pk"), allow_banned=True, allow_deleted=True
        )
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False)
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user

        partial = kwargs.pop("partial", False)
        serializer = UserSerializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(partial=partial)
        except Exception as e:
            return Response({"message": str(e)}, 400)

        return Response(serializer.data)

    @action(methods=["POST"], detail=False)
    def change_email(self, request):

        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if UserService.update_email(serializer.data):
            return Response({"message": "Change email successfully"})
        return Response({"message": "Change email failed"}, status=400)

    @action(methods=["POST"], detail=False)
    def change_password(self, request):
        user = request.user

        serializer = UpdatePasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.save():
            return Response({"message": "Change password successfully"})

        return Response({"message": "Change password failed"}, status=400)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        pk = user.pk

        if user.role in (Roles.ADMIN, Roles.STAFF):
            pk = kwargs.get("pk")

        if UserService.delete(pk):
            return Response({"message": "Delete successfully"})

        return Response({"message": "Delete failed"}, status=400)

    @action(methods=["POST"], detail=True)
    def restore(self, request, **kwargs):
        user = request.user
        if user.role not in (Roles.ADMIN, Roles.STAFF):
            return Response(
                {"message": "You do not have permission to restore user"}, status=403
            )

        pk = kwargs.get("pk")
        if UserService.restore(pk):
            return Response({"message": "Restore successfully"})
        return Response({"message": "Restore failed"}, status=400)

    @action(methods=["POST"], detail=True)
    def ban(self, request, **kwargs):
        user = request.user
        if user.role not in (Roles.ADMIN, Roles.STAFF):
            return Response(
                {"message": "You do not have permission to ban user"}, status=403
            )

        pk = kwargs.get("pk")
        if UserService.ban(pk):
            return Response({"message": "Ban user successfully"})
        return Response({"message": "Ban failed"}, status=400)

    @action(methods=["POST"], detail=True)
    def unban(self, request, **kwargs):
        user = request.user
        if user.role not in (Roles.ADMIN, Roles.STAFF):
            return Response(
                {"message": "You do not have permission to unban user"}, status=403
            )

        pk = kwargs.get("pk")
        if UserService.unban(pk):
            return Response({"message": "Unban user successfully"})
        return Response({"message": "Unban failed"}, status=400)

    @action(methods=["POST"], detail=True)
    def update_role(self, request, **kwargs):
        pk = kwargs.get("pk")
        instance = UserService.get(pk)

        user = request.user

        serializer = UpdateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if UserService.update_role(user, instance, role=serializer.data.get("role")):
            return Response({"message": "Update role successfully"})

        return Response({"message": "Update role failed"}, status=400)

    def list(self, request: Request, *args, **kwargs):
        if request.user.role not in (Roles.ADMIN, Roles.STAFF):
            return self.me(request)

        query = QueryUserSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        users = ESUserService.search(query.data)

        return Response(users)
