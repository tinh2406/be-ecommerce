from django.core.cache import cache
from django.db import models
from django.utils import timezone

from core.managers import BaseTimeManager
from core.models.soft_delete_model import SoftDeleteModel


class BaseTimeModel(SoftDeleteModel):
    objects = BaseTimeManager()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

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

    class Meta:
        abstract = True
