from django.core.cache import cache
from django.db import models
from django.utils import timezone

from core.managers import BaseCacheManager


class BaseTimeModel(models.Model):
    objects = BaseCacheManager()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    key = ""
    cache_key_fields: list[str] = []
    cache_time = 60

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        assert self.key is not None, "Key is required"
        self.updated_at = timezone.now()
        for field in self.cache_key_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        assert self.key is not None, "Key is required"
        for field in self.cache_key_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().delete(using, keep_parents)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        return self.save()

    def restore(self):
        self.deleted_at = None
        return self.save()

    class Meta:
        abstract = True
