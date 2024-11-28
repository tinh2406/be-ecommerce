from conversations.serializers import SimpleConversationSerializer
from conversations.services import (
    ConversationService,
    ESConversationService,
    UnReadService,
)
from core.services import BaseDeleteDomain, BaseRetrieveDomain


class ConversationDomain(BaseRetrieveDomain, BaseDeleteDomain):

    main_service = ConversationService

    @classmethod
    def update(cls, instance, validated_data):
        ConversationService.update(instance, validated_data)

        serializer = SimpleConversationSerializer(instance)
        ESConversationService.index.delay(serializer.data)

        return instance

    @classmethod
    def on_delete_success(cls, pk):
        ESConversationService.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESConversationService.restore.delay(pk)

    @classmethod
    def search_conversation(cls, query_params, user_id):
        data = ESConversationService.search(query_params)

        conversations = [
            {
                **conversation,
                "un_read_count": UnReadService.get_or_create(
                    conversation.id, user_id
                ).total,
            }
            for conversation in data.pop("data")
        ]

        return {**data, "data": conversations}

    @classmethod
    def search_user(cls, query_params):
        data = ConversationService.list_user(query_params)

        return data

    @classmethod
    def retrieve(cls, pk, user_id):
        conversation = ConversationService.get(pk)
        un_read = UnReadService.get_or_create(pk, user_id)
        return conversation, un_read.total
