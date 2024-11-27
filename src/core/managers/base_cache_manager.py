import pickle

from django.core.cache import cache
from django.db.models import Manager


class BaseCacheManager(Manager):

    def get(self, related_fields=None, *args, **kwargs):
        if len(kwargs) != 1:
            return super(Manager, self).get(*args, **kwargs)

        key, value = kwargs.popitem()
        cache_key_fields = self.model.cache_key_fields
        if key not in cache_key_fields:
            return super(Manager, self).get(*args, **kwargs)

        cache_key = self.model.key
        cache_time = self.model.cache_time

        assert cache_key is not None, "Key is required"

        pickled_object = cache.get(f"{cache_key}{value}")
        if pickled_object:
            obj = pickle.loads(pickled_object)
        else:
            if not related_fields:
                obj = super(Manager, self).get(**{key: value})
            elif type(related_fields) is list:
                obj = (
                    super(Manager, self)
                    .prefetch_related(*related_fields)
                    .get(**{key: value})
                )
            else:
                obj = (
                    super(Manager, self)
                    .select_related(related_fields)
                    .get(**{key: value})
                )

            pickled_object = pickle.dumps(obj)

        for field in cache_key_fields:
            att_value = str(getattr(obj, field))
            cache.set(f"{cache_key}{att_value}", pickled_object, timeout=cache_time)

        return obj

    def update(self, **kwargs):
        cache_key = self.model.key
        cache_key_fields = self.model.cache_key_fields

        assert cache_key is not None, "Key is required"

        for field in cache_key_fields:
            cache.delete(f"{self.key}{getattr(self, field)}")

        return super(Manager, self).update(**kwargs)
