from rest_framework.serializers import CharField, ModelSerializer

from conversations.models import Message
from core.utils import BaseQuerySerializer


class MessageSerializer(ModelSerializer):

    conversation_id = CharField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ["id", "sender", "conversation", "created_at", "updated_at"]


class QueryMessageSerializer(BaseQuerySerializer):
    conversation_id = CharField(max_length=255)
