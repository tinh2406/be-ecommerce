from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from conversations.serializers import ConversationSerializer
from conversations.serializers.conversation_serializer import (
    QueryConversationSerializer,
    QueryUserSerializer,
)
from conversations.services import ConversationService
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

        ConversationService.update(conversation, serializer.validated_data)
        return Response(ConversationSerializer(conversation).data)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = ConversationService.get(pk)

        if conversation.sender_id != request.user.id:
            return Response(
                {"detail": "You are not allowed to delete this conversation"},
                status=403,
            )

        ConversationService.delete(pk)
        return Response(status=204)

    @action(detail=False, methods=["GET"])
    def restore(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = ConversationService.get(pk)

        if conversation.sender_id != request.user.id:
            return Response(
                {"detail": "You are not allowed to delete this conversation"},
                status=403,
            )

        ConversationService.restore(pk)
        return Response(status=204)

    def list(self, request, *args, **kwargs):
        query_params = request.query_params
        query_serializer = QueryConversationSerializer(data=query_params)
        query_serializer.is_valid(raise_exception=True)

        user = request.user
        if user.role == Roles.CUSTOMER:
            query_serializer.validated_data["user_id"] = user.id

        data = ConversationService.search_conversation(
            query_serializer.validated_data, request.user.id
        )

        return Response(data)

    @action(detail=False, methods=["GET"])
    def list_user(self, request, *args, **kwargs):

        if request.user.role == Roles.CUSTOMER:
            return Response(
                {"detail": "You are not allowed to view this endpoint"}, status=403
            )

        query_params = request.query_params
        query_serializer = QueryUserSerializer(data=query_params)
        query_serializer.is_valid(raise_exception=True)

        data = ConversationService.search_user(query_serializer.validated_data)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        conversation, unread = ConversationService.retrieve(
            kwargs.get("pk"), request.user.id
        )

        if (
            conversation.sender_id != request.user.id
            and request.user.role == Roles.CUSTOMER
        ):
            return Response(
                {"detail": "You are not allowed to view this conversation"}, status=403
            )

        serializer = ConversationSerializer(conversation)
        return Response({**serializer.data, "un_read_count": unread.total})
