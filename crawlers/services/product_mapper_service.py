from typing import Union

from rest_framework.exceptions import NotFound

from crawlers.models import ProductMapper


class ProductMapperService:

    @classmethod
    def create(cls, validated: dict) -> ProductMapper:
        mapper = ProductMapper.objects.create(**validated)
        return mapper

    @classmethod
    def update(cls, instance: ProductMapper, validated: dict) -> ProductMapper:

        for key, value in validated.items():
            setattr(instance, key, value)
        instance.save()

        return instance

    @classmethod
    def get(
        cls, pk: int, raise_exception: bool = True, allow_deleted: bool = False
    ) -> Union["ProductMapper", None]:
        try:
            mapper = ProductMapper.objects.get(id=pk)
            if not allow_deleted and mapper.deleted_at:
                raise NotFound("Mapper not found")
            return mapper
        except ProductMapper.DoesNotExist:
            if raise_exception:
                raise NotFound("Mapper not found")
            return None

    @classmethod
    def delete(cls, pk):
        instance = cls.get(pk)
        instance.soft_delete()
        return True

    @classmethod
    def restore(cls, pk):
        instance = cls.get(pk, allow_deleted=True)
        instance.restore()
        return True

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):

        query_set = ProductMapper.objects.all()

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
