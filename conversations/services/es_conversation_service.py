from celery import shared_task
from django.utils import timezone
from elasticsearch_dsl import Range
from elasticsearch_dsl.query import Exists

from conversations.document import ConversationDocument
from core.services import BaseESService
from users.services import ESUserService


class ESConversationService(BaseESService):

    @staticmethod
    @shared_task
    def index(object: dict):
        conversation_doc = ConversationDocument(
            meta={"id": object.get("id")},
            id=object.get("id"),
            name=object.get("name"),
            sender_id=object.get("sender_id"),
            last_message_id=object.get("last_message_id"),
            last_message_content=object.get("last_message_content"),
            created_at=object.get("created_at"),
            updated_at=object.get("updated_at"),
        )
        return conversation_doc.save()

    @staticmethod
    @shared_task
    def soft_delete(pk):
        conversation_doc = ConversationDocument(meta={"id": pk})
        return conversation_doc.update(deleted_at=timezone.now())

    @staticmethod
    @shared_task
    def restore(pk):
        conversation_doc = ConversationDocument(meta={"id": pk})
        return conversation_doc.update(deleted_at=None)

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):
        search = ConversationDocument.search()

        keyword = query_params.get("keyword")
        is_deleted = query_params.get("is_deleted")
        delete_from = query_params.get("delete_from")
        delete_to = query_params.get("delete_to")
        created_from = query_params.get("created_from")
        created_to = query_params.get("created_to")
        sender_id = query_params.get("sender_id")
        order_by = query_params.get("order_by") or "updated_at"
        order_type = query_params.get("order_type") or "desc"
        page_size = query_params.get("page_size") or 10
        page = query_params.get("page") or 1
        skip = page_size * (page - 1)

        if is_deleted is not None:
            query = (
                Exists(field="deleted_at")
                if is_deleted
                else ~Exists(field="deleted_at")
            )
            search = search.query(query)

            if delete_from:
                search = search.query(Range(deleted_at={"gte": delete_from}))
            if delete_to:
                search = search.query(Range(deleted_at={"lte": delete_to}))

        if keyword:
            sender_ids = [
                hit.meta.id
                for hit in ESUserService.search({"keyword": keyword}, paginate=False)
            ]

            search = search.query(
                {
                    "bool": {
                        "should": [
                            {"terms": {"sender_id.keyword": sender_ids}},
                            {"multi_match": {"query": keyword, "fields": ["name"]}},
                        ]
                    }
                }
            )
        if sender_id:
            search = search.query({"term": {"sender_id.keyword": sender_id}})
        if created_from:
            search = search.query(Range(created_at={"gte": created_from}))
        if created_to:
            search = search.query(Range(created_at={"lte": created_to}))
        if order_by:
            search = search.sort({order_by: {"order": order_type}})
        if paginate:
            search = search[skip : skip + page_size]

        response = search.execute()

        conversations = [conversation for conversation in response.hits]

        if paginate:
            return {
                "page_count": (response.hits.total.value - 1) // page_size + 1,
                "item_count": response.hits.total.value,
                "page_size": page_size,
                "page": page,
                "data": conversations,
            }

        return conversations
