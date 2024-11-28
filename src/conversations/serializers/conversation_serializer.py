from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateTimeField,
    ModelSerializer,
)

from conversations.constants import ConversationOrderChoices
from conversations.models import Conversation
from conversations.serializers.message_serializer import MessageSerializer
from core.utils import BaseQuerySerializer
from users.serializers.simple_user_serializer import SimpleUserSerializer


class ConversationSerializer(ModelSerializer):

    last_message = MessageSerializer(read_only=True)
    sender = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "last_message", "sender"]


class QueryConversationSerializer(BaseQuerySerializer):

    is_deleted = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)
    sender_id = CharField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(
        allow_null=True, required=False, choices=ConversationOrderChoices
    )


class QueryUserSerializer(BaseQuerySerializer):

    # override
    order_by = ChoiceField(
        allow_null=True, required=False, choices=["conversation_count", "name"]
    )


class SimpleConversationSerializer(ModelSerializer):

    class Meta:
        model = Conversation
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["sender_id"] = instance.sender.id
        if instance.last_message:
            ret["last_message_id"] = instance.last_message.id
            ret["last_message_content"] = instance.last_message.content
        return ret
