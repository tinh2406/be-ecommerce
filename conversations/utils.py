from rest_framework.serializers import ModelSerializer

from conversations.models import Conversation


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
