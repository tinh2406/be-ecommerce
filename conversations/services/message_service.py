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

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):
        query_set = Message.objects.all()

        conversation_id = query_params.get("conversation_id")
        keyword = query_params.get("keyword")
        page_size = query_params.get("page_size") or 10
        page = query_params.get("page") or 1
        skip = page_size * (page - 1)

        query_set = query_set.filter(conversation_id=conversation_id)

        if keyword:
            query_set = query_set.filter(content__icontains=keyword)

        query_set = query_set.order_by("-created_at")

        if paginate:
            count = query_set.count()
            meta = {
                "item_count": count,
                "page": page,
                "page_size": page_size,
                "page_count": count // page_size + 1,
            }
            query_set = query_set[skip : skip + page_size]
            return query_set, meta

        return query_set
