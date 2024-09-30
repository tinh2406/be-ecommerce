from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.constants import Roles
from users.serializers import UserSerializer, ChangeEmailSerializer
from users.services import UserService


class UserViewSet(ModelViewSet):

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.get_id == kwargs.get('pk'):
            return self.me(request)
        if user.role not in (Roles.ADMIN, Roles.STAFF):
            return Response({
                'message': 'You do not have permission to access this user'
            }, status=403)

        instance = UserService.get(kwargs.get('pk'), allow_banned=True, allow_deleted=True)
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user

        partial = kwargs.pop('partial', False)
        serializer = UserSerializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=partial)

        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def change_email(self, request):

        serializer = ChangeEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if UserService.update_email(serializer.data):
            return Response({
                'message': 'Change email successfully'
            })
        return Response({
            'message': 'Change email failed'
        }, status=400)
