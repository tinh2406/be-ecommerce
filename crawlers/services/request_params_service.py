from typing import Union

from rest_framework.exceptions import NotFound

from crawlers.models import RequestParams


class RequestParamsService:

    @classmethod
    def create(cls, validated: dict) -> RequestParams:
        request_params = RequestParams.objects.create(
            headers=validated.get("headers"),
            params=validated.get("params"),
        )
        return request_params

    @classmethod
    def update_saved_product(cls, pk, skip):
        instance = cls.get(pk, raise_exception=True)
        if instance:
            instance.params["skip"] = skip
            instance.save()
        return instance

    @classmethod
    def get(
        cls, pk: int, raise_exception: bool = True, allow_deleted: bool = False
    ) -> Union["RequestParams", None]:
        try:
            request_params = RequestParams.objects.get(id=pk)
            if not allow_deleted and request_params.deleted_at:
                raise NotFound("RequestParams not found")
            return request_params
        except RequestParams.DoesNotExist:
            if raise_exception:
                raise NotFound("RequestParams not found")
            return None

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.delete()
        return True
