from core.managers import BaseCacheManager


class BaseTimeManager(BaseCacheManager):

    def get_with_allow_deleted(self, related_fields=None, *args, **kwargs):
        return super().get(related_fields, *args, **kwargs)

    def get(self, related_fields=None, *args, **kwargs):
        obj = self.get_with_allow_deleted(related_fields, *args, **kwargs)
        if not obj.deleted_at:
            return obj
        return None
