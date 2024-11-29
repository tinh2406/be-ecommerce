from rest_framework.serializers import CharField, ModelSerializer

from conversations.domains import MessageDomain
from conversations.models import Message
from core.utils import BaseQuerySerializer


class MessageSerializer(ModelSerializer):

    conversation_id = CharField(write_only=True, required=False)

    def to_representation(self, instance):
        params = None
        if instance.params:
            params = MessageDomain.get_params(instance.params)
            params.pop("_id", None)
        data = super().to_representation(instance)
        data["params"] = params

        return data

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ["id", "sender", "conversation", "created_at", "updated_at"]


class QueryMessageSerializer(BaseQuerySerializer):
    conversation_id = CharField(max_length=255)
