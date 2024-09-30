from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.constants import Roles
from users.serializers import UserSerializer
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