from conversations.domains import ConversationDomain, ESConversationDomain, UnReadDomain
from conversations.serializers import SimpleConversationSerializer
from core.services import BaseDeleteService, BaseRetrieveService


class ConversationService(BaseDeleteService, BaseRetrieveService):

    main_domain = ConversationDomain

    @classmethod
    def update(cls, instance, validated_data):
        ConversationDomain.update(instance, validated_data)

        serializer = SimpleConversationSerializer(instance)
        ESConversationDomain.index.delay(serializer.data)

        return instance

    @classmethod
    def on_delete_success(cls, pk):
        ESConversationDomain.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESConversationDomain.restore.delay(pk)

    @classmethod
    def search_conversation(cls, query_params, user_id):
        data = ESConversationDomain.search(query_params)

        conversations = [
            {
                **conversation,
                "un_read_count": ESConversationDomain.get_or_create(
                    conversation.id, user_id
                ).total,
            }
            for conversation in data.pop("data")
        ]

        return {**data, "data": conversations}

    @classmethod
    def search_user(cls, query_params):
        data = ConversationDomain.list_user(query_params)

        return data

    @classmethod
    def retrieve(cls, pk, user_id):
        conversation = ConversationDomain.get(pk)
        un_read = UnReadDomain.get_or_create(pk, user_id)
        return conversation, un_read.total
