from typing import Any


class BaseRetrieveService:
    main_domain: Any = None

    @classmethod
    def get(cls, pk):
        assert cls.main_domain, "main_domain is not set"
        return cls.main_domain.get(pk)
