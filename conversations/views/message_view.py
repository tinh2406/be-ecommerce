from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from conversations.serializers import MessageSerializer
from conversations.services import MessageService
from users.constants import Roles


class MessageViewSet(ModelViewSet):

    def create(self, request, *args, **kwargs):

        user_id = request.user.id

        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if request.user.role == Roles.CUSTOMER:
            validated_data.pop("type", None)
            validated_data.pop("is_bot", None)

        message = MessageService.create(**serializer.validated_data, user_id=user_id)
        return Response(MessageSerializer(message).data)
