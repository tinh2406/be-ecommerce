import threading
from time import sleep

from bson import ObjectId
from django.conf import settings
from django_eventstream import send_event
from pymongo import MongoClient
from rest_framework.exceptions import NotFound

from chatbot.services.chatbot import ChatbotService
from conversations.constants import MessageRoles
from conversations.models import Message
from core.services import BaseService

from .conversation_service import ConversationService
from .un_read_service import UnReadService

# Khởi tạo MongoClient và kết nối đến MongoDB
client = MongoClient(
    f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@nqt_server:27017/"
)
db = client[settings.MONGO_DATABASE]
message_params_collection = db["message_params"]


class MessageService(BaseService):
    manager = Message.objects

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs) -> Message | None:
        try:
            instance = Message.objects.prefetch_related("conversation").get(id=pk)
            if instance:
                return instance
        except Exception:
            pass
        if raise_exception:
            raise NotFound("Object not found")
        return None

    @classmethod
    def create(cls, **kwargs):
        conversation_id = kwargs.pop("conversation_id", None)
        sender_id = kwargs.pop("user_id")

        conversation = ConversationService.get(conversation_id, raise_exception=False)
        if not conversation:
            conversation = ConversationService.create(
                validated={
                    "name": "New conversation",
                    "sender_id": sender_id,
                }
            )
            cv_thread = threading.Thread(
                target=cls.update_conversation_name,
                args=(conversation.id, kwargs.get("content")),
            )
            cv_thread.start()

        params = kwargs.pop("params", None)
        if params:
            kwargs["params"] = cls.create_params(**params)

        message = Message.objects.create(
            **kwargs, sender_id=sender_id, conversation_id=conversation.id
        )
        ConversationService.update_last_message(
            conversation.id, {"last_message_id": message.id}
        )

        if message.role == MessageRoles.USER:

            thread = threading.Thread(
                target=cls.create_bot_message,
                args=(conversation.id, message.content),
            )
            thread.start()
        else:
            UnReadService.add_unread(conversation_id, sender_id)
            cls.create_notify(sender_id, conversation.id, message.id)

        return message

    @classmethod
    def create_bot_message(cls, conversation_id, question):
        conversation = ConversationService.get(conversation_id)
        histories = cls.search(
            {"conversation_id": conversation_id, "page_size": 10, "page": 1},
            paginate=False,
        )
        messages = [
            {"role": history.role, "content": history.content} for history in histories
        ]

        response, navigates, actions, is_contact_support = (
            ChatbotService.generate_response(messages, question)
        )
        print(response, navigates, actions, is_contact_support)

        if is_contact_support:
            # TODO: Send message to staff
            pass

        params = cls.create_params(navigates=navigates, actions=actions)

        message = Message.objects.create(
            conversation_id=conversation_id,
            role=MessageRoles.BOT,
            content=response,
            params=params,
        )
        UnReadService.add_unread(conversation_id, conversation.sender_id)
        ConversationService.update_last_message(
            conversation_id, {"last_message_id": message.id}
        )
        cls.create_notify(conversation.sender_id, conversation.id, message.id)

        return message

    @classmethod
    def update_conversation_name(cls, conversation_id, message):
        conversation = ConversationService.get(conversation_id)
        sleep(5)
        # name = ChatbotService.generate_name_for_conversation(message)
        name = "Updated name conversation"
        print(name)
        ConversationService.update(conversation, {"name": name})
        cls.conversation_name_change_notify(conversation.sender_id, conversation.id)
        return conversation

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
        query_set = query_set[skip : skip + page_size]

        if paginate:
            count = query_set.count()
            meta = {
                "item_count": count,
                "page": page,
                "page_size": page_size,
                "page_count": count // page_size + 1,
            }
            return query_set, meta

        return query_set

    @classmethod
    def conversation_name_change_notify(cls, sender_id, conversation_id):
        send_event(
            f"user-{sender_id}",
            "message",
            {"id": conversation_id, "type": "CONVERSATION_NAME_CHANGE"},
        )

    @classmethod
    def create_notify(cls, sender_id, conversation_id, message_id):
        send_event(
            f"user-{sender_id}", "message", {"id": message_id, "type": "NEW_MESSAGE"}
        )

        send_event(
            f"user-{sender_id}",
            "message",
            {"id": conversation_id, "type": "CONVERSATION_UPDATE"},
        )

    @classmethod
    def create_params(cls, **kwargs):
        return message_params_collection.insert_one(kwargs).inserted_id

    @classmethod
    def get_params(cls, id):
        return message_params_collection.find_one({"_id": ObjectId(id)})
