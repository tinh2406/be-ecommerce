import uuid

from django.db.models import CASCADE, BooleanField, CharField, ForeignKey, UUIDField

from conversations.constants import MessageTypes
from core.models import BaseTimeModel


class Message(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = ForeignKey(
        "Conversation", on_delete=CASCADE, related_name="messages"
    )
    is_bot = BooleanField(default=False)
    sender = ForeignKey("users.User", on_delete=CASCADE)
    content = CharField(max_length=255)
    type = CharField(choices=MessageTypes.CHOICES, max_length=20, null=True, blank=True)

    cache_key_fields = ["id"]
    key = "message_"

    class Meta:
        db_table = "messages"
