import uuid

from django.db.models import CASCADE, ForeignKey, IntegerField, Model, UUIDField


class UnRead(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = ForeignKey(
        "conversations.Conversation",
        on_delete=CASCADE,
        related_name="unread_messages",
    )

    user = ForeignKey("users.User", on_delete=CASCADE, related_name="unread_messages")
    total = IntegerField(default=0)

    class Meta:
        db_table = "unread_messages"
