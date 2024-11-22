from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from conversations.serializers import ConversationSerializer
from conversations.serializers.conversation_serializer import (
    QueryConversationSerializer,
    QueryUserSerializer,
)
from conversations.services import (
    ConversationService,
    ESConversationService,
    UnReadService,
)
from users.constants import Roles


class ConversationViewSet(ModelViewSet):

    def update(self, request, *args, **kwargs):
        conversation = ConversationService.get(kwargs.get("pk"))

        if conversation.sender_id != request.user.id:
            return Response(
                {"detail": "You are not allowed to update this conversation"},
                status=403,
            )

        serializer = ConversationSerializer(conversation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        conversation = ConversationService.get(kwargs.get("pk"))

        if conversation.sender_id != request.user.id:
            return Response(
                {"detail": "You are not allowed to delete this conversation"},
                status=403,
            )

        ConversationService.delete(kwargs.get("pk"))
        return Response(status=204)

    @action(detail=False, methods=["GET"])
    def restore(self, request, *args, **kwargs):
        ConversationService.restore(kwargs.get("pk"))
        return Response(status=204)

    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        query_serializer = QueryConversationSerializer(data=query_params)
        query_serializer.is_valid(raise_exception=True)
        data = ESConversationService.search(
            query_serializer.validated_data, paginate=True
        )

        conversations = [
            {
                **conversation,
                "un_read_count": UnReadService.get_or_create(
                    conversation.id, request.user.id
                ).total,
            }
            for conversation in data.pop("data")
        ]

        return Response({**data, "data": conversations})

    @action(detail=False, methods=["GET"])
    def list_user(self, request, *args, **kwargs):

        if request.user.role == Roles.CUSTOMER:
            return Response(
                {"detail": "You are not allowed to view this endpoint"}, status=403
            )

        query_params = request.query_params
        query_serializer = QueryUserSerializer(data=query_params)
        query_serializer.is_valid(raise_exception=True)
        data = ConversationService.list_user(query_serializer.validated_data)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        conversation = ConversationService.get(kwargs.get("pk"))

        if (
            conversation.sender_id != request.user.id
            and request.user.role == Roles.CUSTOMER
        ):
            return Response(
                {"detail": "You are not allowed to view this conversation"}, status=403
            )

        serializer = ConversationSerializer(conversation)
        unread = UnReadService.get_or_create(conversation.id, request.user.id)
        return Response({**serializer.data, "un_read_count": unread.total})
