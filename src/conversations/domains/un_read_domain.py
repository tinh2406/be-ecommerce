from conversations.models import UnRead


class UnReadDomain:

    @classmethod
    def add_unread(cls, conversation_id, user_id, amount=1):
        try:
            unread = UnRead.objects.get(
                conversation_id=conversation_id, user_id=user_id
            )
            unread.total += amount
            unread.save()
        except Exception:
            try:
                unread = UnRead.objects.create(
                    conversation_id=conversation_id, user_id=user_id, total=1
                )
            except Exception:
                return 0

        return unread

    @classmethod
    def read_all(cls, conversation_id, user_id):
        unread = cls.get_or_create(conversation_id, user_id)
        unread.total = 0
        unread.save()
        return unread

    @classmethod
    def get_or_create(cls, conversation_id, user_id):
        try:
            unread = UnRead.objects.get(
                conversation_id=conversation_id, user_id=user_id
            )
        except Exception:
            unread = UnRead.objects.create(
                conversation_id=conversation_id, user_id=user_id, total=0
            )

        return unread
