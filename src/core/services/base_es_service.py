class BaseESService:

    @staticmethod
    def index(object: dict):
        raise NotImplementedError

    @staticmethod
    def soft_delete(pk):
        raise NotImplementedError

    @staticmethod
    def restore(pk):
        raise NotImplementedError

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):
        raise NotImplementedError
