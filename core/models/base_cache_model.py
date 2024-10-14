from django.core.cache import cache
from django.db import models

from core.managers import BaseCacheManager


class BaseCacheModel(models.Model):
    objects = BaseCacheManager()

    key = ""
    cache_key_fields: list[str] = []
    cache_time = 60

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        assert self.key is not None, "Key is required"
        for field in self.cache_key_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().save(*args, force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        assert self.key is not None, "Key is required"
        for field in self.cache_key_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().delete(using, keep_parents)

    class Meta:
        abstract = True
