from conversations.models import Message
from conversations.services.conversation_service import ConversationService
from core.services import BaseService


class MessageService(BaseService):

    model = Message

    @classmethod
    def create(cls, **kwargs):
        conversation_id = kwargs.pop("conversation_id", None)
        sender_id = kwargs.pop("user_id")

        conversation = ConversationService.get(conversation_id, raise_exception=False)
        if not conversation:
            conversation = ConversationService.create(
                validated={
                    "name": "Test new conversation",
                    "sender_id": sender_id,
                }
            )
        message = Message.objects.create(
            **kwargs, sender_id=sender_id, conversation_id=conversation.id
        )
        ConversationService.update(conversation, {"last_message_id": message.id})
        return message

    @classmethod
    def update(cls, instance: Message, validated: dict):
        last_message = instance.conversation.last_message
        if last_message.id == instance.id:
            instance.content = validated.get("content")
            instance.type = validated.get("type")
            instance.save()
        return instance
