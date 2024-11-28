from core.domains import BaseService
from crawlers.models import RequestParams


class RequestParamsService(BaseService):

    manager = RequestParams.objects

    @classmethod
    def create(cls, validated: dict) -> RequestParams:
        request_params = RequestParams.objects.create(
            headers=validated.get("headers"),
            params=validated.get("params"),
        )
        return request_params

    @classmethod
    def update_params(cls, pk, params):
        instance = cls.get(pk, raise_exception=True)
        if instance:
            instance.params = params
            instance.save()
        return instance
