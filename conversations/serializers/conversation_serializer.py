from rest_framework.serializers import ModelSerializer

from conversations.models import Conversation
from conversations.services import ConversationService


class ConversationSerializer(ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "last_message", "sender"]

    def update(self, instance, validated_data):
        ConversationService.update(instance, validated_data)
        return instance
