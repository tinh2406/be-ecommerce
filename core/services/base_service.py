from typing import Type

from rest_framework.exceptions import NotFound

from core.models import BaseTimeModel
from core.services.base_es_service import BaseESService


class BaseService:

    model: Type[BaseTimeModel]
    es_service: Type[BaseESService] | None = None

    @classmethod
    def create(cls, validated: dict):
        obj = cls.model.objects.create(**validated)
        return obj

    @classmethod
    def update(cls, instance, validated: dict):

        for key, value in validated.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs):
        assert cls.model, "Model not defined"

        try:
            object = cls.model.objects.get(id=pk)
            if object:
                return object
        except cls.model.DoesNotExist:
            pass
        if raise_exception:
            raise NotFound("Object not found")
        return None

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.soft_delete()

        if cls.es_service:
            cls.es_service.soft_delete.delay(str(pk))
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.model.objects.get_with_allow_deleted(id=pk)
        instance.restore()

        if cls.es_service:
            cls.es_service.restore.delay(str(pk))
        return True
