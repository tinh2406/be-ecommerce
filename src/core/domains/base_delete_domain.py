from typing import Any


class BaseDeleteDomain:
    main_service: Any = None

    @classmethod
    def on_delete_success(cls, pk):
        pass

    @classmethod
    def on_restore_success(cls, pk):
        pass

    @classmethod
    def delete(cls, pk) -> bool:
        assert cls.main_service, "main_service is not set"
        if cls.main_service.delete(pk):
            cls.on_delete_success(pk)
            return True
        return False

    @classmethod
    def restore(cls, pk) -> bool:
        assert cls.main_service, "main_service is not set"

        if cls.main_service.restore(pk):
            cls.on_restore_success(pk)
            return True
        return False
