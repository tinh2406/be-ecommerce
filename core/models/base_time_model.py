import pickle

from django.core.cache import cache
from django.db import models
from django.db.models import Manager
from django.utils import timezone


class BaseTimeModel(models.Model):
    objects = Manager
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    key = ""
    cache_fields: list[str] = []
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
        self.updated_at = timezone.now()
        for field in self.cache_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().save(*args, force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        assert self.key is not None, "Key is required"
        for field in self.cache_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")
        return super().delete(using, keep_parents)

    @classmethod
    def cache_load(cls, **kwargs):
        assert cls.key is not None, "Key is required"
        key, value = kwargs.popitem()
        if key == "pk":
            key = "id"

        pickled_object = cache.get(f"{cls.key}{value}")
        if pickled_object:
            obj = pickle.loads(pickled_object)
        else:
            obj = cls.objects.get(**{key: value})
            pickled_object = pickle.dumps(obj)

        for field in cls.cache_fields:
            att_value = str(getattr(obj, field))

            cache.set(f"{cls.key}{att_value}", pickled_object, timeout=cls.cache_time)
        return obj

    class Meta:
        abstract = True
