from django.db.models import Model

from core.services import BaseService
from crawlers.models import ProductMapper, ProductsMapper


class SearchMapperService:

    model: Model

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):
        assert cls.model, "Model not defined"

        query_set = cls.model.objects.all()

        # Lấy các tham số truy vấn
        keyword = query_params.get("keyword")
        is_deleted = query_params.get("is_deleted")
        created_from = query_params.get("created_from")
        created_to = query_params.get("created_to")
        delete_from = query_params.get("delete_from")
        delete_to = query_params.get("delete_to")
        order_by = query_params.get("order_by") or "created_at"
        order_type = query_params.get("order_type") or "desc"
        page_size = query_params.get("page_size") or 10
        page = query_params.get("page") or 1
        skip = (page - 1) * page_size  # Tính toán skip từ page và page_size

        if is_deleted is not None:
            query_set = query_set.filter(deleted_at__isnull=not is_deleted)
            if delete_from:
                query_set = query_set.filter(deleted_at__gte=delete_from)
            if delete_to:
                query_set = query_set.filter(deleted_at__lte=delete_to)

        # Lọc theo các thuộc tính khác
        if keyword:
            query_set = query_set.filter(name__icontains=keyword)

        if created_from:
            query_set = query_set.filter(created_at__gte=created_from)
        if created_to:
            query_set = query_set.filter(created_at__lte=created_to)

        if paginate:
            total = query_set.count()
            query_set = query_set.order_by(
                f"{'-' if order_type=='desc' else ''}{order_by}"
            )[skip : skip + page_size]

            meta = {
                "page_count": (total - 1) // page_size + 1,
                "item_count": total,
                "page_size": page_size,
                "page": page,
            }

            return query_set, meta

        return query_set


class ProductMapperService(BaseService, SearchMapperService):

    manager = ProductMapper.objects


class ProductsMapperService(BaseService, SearchMapperService):

    manager = ProductsMapper.objects
