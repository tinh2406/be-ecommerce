from conversations.models import Message
from conversations.services.conversation_service import ConversationService


class MessageService:
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
        conversation.last_message = message
        conversation.save()
        return message
