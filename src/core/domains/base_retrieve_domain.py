from typing import Any


class BaseRetrieveDomain:
    main_service: Any = None

    @classmethod
    def get(cls, pk):
        assert cls.main_service, "main_service is not set"
        return cls.main_service.get(pk)
