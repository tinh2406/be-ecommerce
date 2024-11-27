import uuid

from django.db.models import CASCADE, CharField, ForeignKey, UUIDField

from core.models import BaseTimeModel


class Conversation(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)
    sender = ForeignKey("users.User", on_delete=CASCADE, related_name="conversations")
    last_message = ForeignKey(
        "Message", on_delete=CASCADE, null=True, blank=True, related_name="last_message"
    )

    cache_key_fields = ["id"]
    key = "conversation_"

    class Meta:
        db_table = "conversations"
