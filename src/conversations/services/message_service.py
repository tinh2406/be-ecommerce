from bson import ObjectId
from django.conf import settings
from django_eventstream import send_event
from pymongo import MongoClient
from rest_framework.exceptions import NotFound

from conversations.constants import MessageRoles
from conversations.models import Message
from core.domains import BaseService

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
        sender_id = kwargs.pop("user_id")
        conversation = kwargs.get("conversation")

        params = kwargs.pop("params", None)
        if params:
            kwargs["params"] = cls.create_params(**params)

        message = Message.objects.create(
            **kwargs, sender_id=sender_id, conversation_id=conversation.id
        )

        return message

    @classmethod
    def create_bot_message(
        cls,
        conversation,
        response,
        is_contact_support=False,
        navigates=None,
        actions=None,
    ):
        if is_contact_support:
            # TODO: Send message to staff
            pass

        params = cls.create_params(navigates=navigates, actions=actions)

        message = Message.objects.create(
            conversation_id=conversation.id,
            role=MessageRoles.BOT,
            content=response,
            params=params,
        )

        return message

    @classmethod
    def update(cls, instance: Message, validated_message: dict):
        last_message = instance.conversation.last_message
        if last_message.id == instance.id:
            instance.content = validated_message.get("content")
            instance.type = validated_message.get("type")
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
