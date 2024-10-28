from rest_framework.exceptions import NotFound

from conversations.models import Conversation
from core.services import BaseService


class ConversationService(BaseService):

    model = Conversation

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs):
        try:
            instance = Conversation.objects.get(id=pk)
            if instance:
                return instance
        except cls.model.DoesNotExist:
            pass
        if raise_exception:
            raise NotFound("Object not found")
        return None

    @classmethod
    def update(cls, instance, validated: dict):
        instance.name = validated.get("name")
        instance.save()
        return instance
