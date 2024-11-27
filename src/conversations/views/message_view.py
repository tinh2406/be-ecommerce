from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from conversations.serializers import MessageSerializer, QueryMessageSerializer
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

    def update(self, request, *args, **kwargs):
        message = MessageService.get(kwargs.get("pk"))

        if message.sender_id != request.user.id:
            return Response(
                {"detail": "You are not allowed to update this message"},
                status=403,
            )

        serializer = MessageSerializer(message, data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if request.user.role == Roles.CUSTOMER:
            validated_data.pop("type", None)
            validated_data.pop("is_bot", None)

        message = MessageService.update(message, serializer.validated_data)

        return Response(MessageSerializer(message).data)

    def list(self, request, *args, **kwargs):
        serializer = QueryMessageSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data, meta = MessageService.search(serializer.validated_data, paginate=True)

        messages = MessageSerializer(data, many=True).data
        return Response({**meta, "data": messages})

    def retrieve(self, request, *args, **kwargs):
        message = MessageService.get(kwargs.get("pk"))

        if (
            request.user.role == Roles.CUSTOMER
            and message.conversation.sender_id != request.user.id
        ):
            return Response(
                {"detail": "You are not allowed to view this message"},
                status=403,
            )

        return Response(MessageSerializer(message).data)
