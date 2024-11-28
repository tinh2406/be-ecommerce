from math import ceil

from django.db import connection
from django_eventstream import send_event
from rest_framework.exceptions import NotFound

from conversations.models import Conversation
from core.domains import BaseDomain
from users.models import User


class ConversationDomain(BaseDomain):

    manager = Conversation.objects

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs) -> Conversation | None:
        try:
            instance = Conversation.objects.get(
                id=pk, related_fields=["last_message", "sender"]
            )
            if instance:
                return instance
        except Exception:
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

        return instance

    @classmethod
    def update_last_message(cls, conversation_id, validated: dict):
        conversation = cls.get(conversation_id)
        if not conversation:
            return

        conversation.last_message_id = (
            validated.get("last_message_id") or conversation.last_message_id
        )
        conversation.save()
        return conversation

    @classmethod
    def list_user(cls, query_params, **kwargs):
        keyword = query_params.get("keyword")
        order_by = query_params.get("order_by") or "name"
        order_type = query_params.get("order_type") or "desc"
        page_size = query_params.get("page_size") or 10
        page = query_params.get("page") or 1
        skip = page_size * (page - 1)

        count_query = """
            SELECT COUNT(*) as total_count
            FROM (
                SELECT users.id
                FROM conversations
                INNER JOIN users ON (
                    conversations.sender_id = users.id
                    AND conversations.deleted_at IS NULL
                )
                {where_clause}
                GROUP BY users.id
                HAVING COUNT(conversations.id) > 0
            ) as subquery
        """

        where_clause = "WHERE users.name LIKE %s" if keyword else ""
        count_query = count_query.format(where_clause=where_clause)

        count_params = [f"%{keyword}%"] if keyword else []
        total_count = connection.cursor().execute(count_query, count_params)

        total_pages = ceil(total_count / page_size)

        query_string = f"""
            SELECT users.id, users.name, profiles.image, users.banned_at, users.deleted_at, COUNT(conversations.id) AS conversation_count
            FROM conversations
            INNER JOIN users ON (
                conversations.sender_id = users.id
                AND conversations.deleted_at IS NULL
            )
            LEFT JOIN profiles ON users.id = profiles.user_id
            {where_clause}
            GROUP BY users.id, users.name
            HAVING COUNT(conversations.id) > 0
            ORDER BY {order_by} {order_type.upper()}
            LIMIT {page_size} OFFSET {skip}
        """

        queryset = User.objects.raw(query_string, count_params)

        results = [
            {
                "id": user.id,
                "name": user.name,
                "conversation_count": user.conversation_count,
                "image": user.image,
                "banned_at": user.banned_at,
                "deleted_at": user.deleted_at,
            }
            for user in queryset
        ]

        return {
            "data": results,
            "item_count": total_count,
            "page_count": total_pages,
            "page_size": page_size,
            "page": page,
        }

    @classmethod
    def conversation_name_change_notify(cls, sender_id, conversation_id):
        send_event(
            f"user-{sender_id}",
            "message",
            {"id": conversation_id, "type": "CONVERSATION_NAME_CHANGE"},
        )
