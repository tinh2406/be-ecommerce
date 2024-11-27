import uuid

from django.db.models import CASCADE, CharField, ForeignKey, TextField, UUIDField

from conversations.constants import MessageRoles, MessageTypes
from core.models import BaseTimeModel


class Message(BaseTimeModel):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = ForeignKey(
        "Conversation", on_delete=CASCADE, related_name="messages"
    )

    sender = ForeignKey("users.User", on_delete=CASCADE, null=True)
    role = CharField(
        max_length=20, choices=MessageRoles.CHOICES, default=MessageRoles.USER
    )
    content = TextField()
    type = CharField(choices=MessageTypes.CHOICES, max_length=20, null=True, blank=True)
    params = CharField(max_length=255, null=True, blank=True)

    cache_key_fields = ["id"]
    key = "message_"

    class Meta:
        db_table = "messages"
