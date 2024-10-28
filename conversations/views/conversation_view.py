from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from conversations.serializers import ConversationSerializer
from conversations.services import ConversationService


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

        conversation.soft_delete()
        return Response(status=204)
