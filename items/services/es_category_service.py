from elasticsearch_dsl.query import Exists, Range, Term

from items.document import CategoryDocument
from items.models import Category


class ESCategoryService:

    @classmethod
    def index(cls, category: Category):
        cate_doc = CategoryDocument(
            meta={"id": str(category.id)},
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
            created_at=category.created_at,
        )
        return cate_doc.save()

    @classmethod
    def update(cls, category: Category):
        cate_doc = CategoryDocument.get(id=str(category.id))
        cate_doc.update(
            name=category.name,
            parent_id=category.parent_id,
            created_at=category.created_at,
            deleted_at=category.deleted_at,
        )
        return cate_doc.save()

    @classmethod
    def delete(cls, pk):
        cate_doc = CategoryDocument.get(id=str(pk))
        return cate_doc.delete()

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):

        search = CategoryDocument.search()

        # Lấy các tham số truy vấn
        keyword = query_params.get("keyword")
        parent_id = query_params.get("parent_id")
        is_deleted = query_params.get("is_deleted")
        created_from = query_params.get("created_from")
        created_to = query_params.get("created_to")
        delete_from = query_params.get("delete_from")
        delete_to = query_params.get("delete_to")
        order_by = (
            query_params.get("order_by")
            if query_params.get("order_by")
            else "created_at"
        )
        order_type = (
            query_params.get("order_type") if query_params.get("order_type") else "desc"
        )
        page_size = query_params.get("page_size", 10)
        page = query_params.get("page", 1)
        skip = query_params.get("skip")

        if is_deleted is not None:
            if is_deleted:
                query = Exists(field="deleted_at")
            else:
                query = ~Exists(field="deleted_at")
            search = search.query(query)
            if delete_from:
                search = search.query(Range(deleted_at={"gte": delete_from}))
            if delete_to:
                search = search.query(Range(deleted_at={"lte": delete_to}))
        else:
            # Lọc những bản ghi không bị xóa
            search = search.filter("bool", must_not=Exists(field="deleted_at"))

        # Lọc theo các thuộc tính khác
        if keyword:
            search = search.query(
                "multi_match", query=keyword, fields=["name"], fuzziness="AUTO"
            )
        if parent_id:
            search = search.query(Term(parent_id=parent_id))
        if created_from:
            search = search.query(Range(created_at={"gte": created_from}))
        if created_to:
            search = search.query(Range(created_at={"lte": created_to}))

        if paginate:
            search = search.sort({order_by: {"order": order_type}})
            search = search[skip : skip + page_size]

        response = search.execute()

        categories = [category for category in response.hits]

        if paginate:
            return {
                "page_count": (response.hits.total.value - 1) // page_size + 1,
                "item_count": response.hits.total.value,
                "page_size": page_size,
                "page": page,
                "data": categories,
            }

        return categories
