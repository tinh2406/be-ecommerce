from rest_framework.exceptions import NotFound

from conversations.models import Conversation
from conversations.services.es_conversation_service import ESConversationService
from conversations.utils import SimpleConversationSerializer
from core.services import BaseService


class ConversationService(BaseService):

    model = Conversation
    es_service = ESConversationService

    @classmethod
    def create(cls, validated: dict):
        obj = super().create(validated)

        serializer = SimpleConversationSerializer(obj)
        ESConversationService.index.delay(serializer.data)
        return obj

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs):
        try:
            instance = Conversation.objects.get(
                id=pk, related_fields=["last_message", "sender"]
            )
            if instance:
                return instance
        except cls.model.DoesNotExist:
            pass
        if raise_exception:
            raise NotFound("Object not found")
        return None

    @classmethod
    def update(cls, instance, validated: dict):
        instance.name = validated.get("name") or instance.name
        instance.last_message_id = (
            validated.get("last_message_id") or instance.last_message_id
        )
        instance.save()

        serializer = SimpleConversationSerializer(instance)
        ESConversationService.index.delay(serializer.data)

        return instance
