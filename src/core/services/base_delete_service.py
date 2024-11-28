from typing import Any


class BaseDeleteService:
    main_domain: Any = None

    @classmethod
    def on_delete_success(cls, pk):
        pass

    @classmethod
    def on_restore_success(cls, pk):
        pass

    @classmethod
    def delete(cls, pk) -> bool:
        assert cls.main_domain, "main_domain is not set"
        if cls.main_domain.delete(pk):
            cls.on_delete_success(pk)
            return True
        return False

    @classmethod
    def restore(cls, pk) -> bool:
        assert cls.main_domain, "main_domain is not set"

        if cls.main_domain.restore(pk):
            cls.on_restore_success(pk)
            return True
        return False
