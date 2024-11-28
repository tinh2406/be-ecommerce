from typing import Type

from rest_framework.exceptions import NotFound

from src.core.managers import BaseTimeManager


class BaseDomain:

    manager: Type[BaseTimeManager]

    @classmethod
    def create(cls, validated: dict):
        assert cls.manager, "Model not defined"

        obj = cls.manager.create(**validated)
        return obj

    @classmethod
    def update(cls, instance, validated: dict):
        for key, value in validated.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    @classmethod
    def get(cls, pk, raise_exception=True, **kwargs):
        assert cls.manager, "Model not defined"

        try:
            instance = cls.manager.get(id=pk)
            if instance:
                return instance
        except Exception:
            pass
        if raise_exception:
            raise NotFound("Object not found")
        return None

    @classmethod
    def delete(cls, pk):
        assert cls.manager, "Manager not defined"

        instance = cls.get(pk)
        instance.soft_delete()

        return True

    @classmethod
    def restore(cls, pk):
        assert cls.manager, "Manager not defined"

        instance = cls.manager.get_with_allow_deleted(id=pk)
        instance.restore()

        return True
