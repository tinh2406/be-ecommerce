from celery import shared_task
from elasticsearch_dsl.query import Bool, Exists, Range, Term

from items.document import ItemDocument


class ESItemService:

    @staticmethod
    @shared_task
    def index(item: dict):
        item_doc = ItemDocument(
            meta={"id": item.get("id")},
            id=item.get("id"),
            name=item.get("name"),
            description=item.get("description"),
            thumbnail=item.get("thumbnail"),
            price=item.get("price"),
            hot_price=item.get("hot_price"),
            category_id=item.get("category_id"),
            created_at=item.get("created_at"),
        )
        return item_doc.save()

    @staticmethod
    @shared_task
    def delete(pk):
        cate_doc = ItemDocument.get(id=str(pk))
        return cate_doc.delete()

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):

        search = ItemDocument.search()

        # Lấy các tham số truy vấn
        keyword = query_params.get("keyword")
        category_id = query_params.get("category_id")
        is_deleted = query_params.get("is_deleted")
        created_from = query_params.get("created_from")
        created_to = query_params.get("created_to")
        price_from = query_params.get("price_from")
        price_to = query_params.get("price_to")
        delete_from = query_params.get("delete_from")
        delete_to = query_params.get("delete_to")
        order_by = query_params.get("order_by") or "_score"
        order_type = query_params.get("order_type") or "desc"
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
                "multi_match",
                query=keyword,
                fields=["name", "description"],
                fuzziness="AUTO",
            )
        if category_id:
            search = search.query(Term(category_id=category_id))
        if created_from:
            search = search.query(Range(created_at={"gte": created_from}))
        if created_to:
            search = search.query(Range(created_at={"lte": created_to}))
        if price_from:
            search = search.query(Range(price={"gte": price_from}))
        if price_to:
            search = search.query(
                Bool(
                    should=[
                        # Điều kiện nếu có "hot_price"
                        Range(hot_price={"lte": price_to}),
                        # Điều kiện nếu không có "hot_price"
                        Bool(
                            must_not=Exists(field="hot_price"),
                            filter=Range(price={"lte": price_to}),
                        ),
                    ],
                    minimum_should_match=1,  # Cần ít nhất một điều kiện phải khớp
                )
            )
        if paginate:
            if order_by == "price":
                search = search.sort(
                    {
                        "hot_price": {"order": order_type, "missing": "_last"},
                        "price": {"order": order_type},
                    }
                )
            else:
                search = search.sort({order_by: {"order": order_type}})
            search = search[skip : skip + page_size]

        response = search.execute()

        items = [item for item in response.hits]

        if paginate:
            return {
                "page_count": (response.hits.total.value - 1) // page_size + 1,
                "item_count": response.hits.total.value,
                "page_size": page_size,
                "page": page,
                "data": items,
            }

        return items
