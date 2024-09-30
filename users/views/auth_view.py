from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from users.serializers import RegisterSerializer

class AuthViewSet(ViewSet):

    permission_classes = []
    authentication_classes = []

    @action(methods=['POST'], detail=False)
    def register(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Register successfully'
        })
