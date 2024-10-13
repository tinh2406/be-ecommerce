from celery import shared_task
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl.query import Bool, Exists, MultiMatch, Range, Term

from products.document import ProductDocument


class ESProductService:

    @staticmethod
    @shared_task
    def index(product: dict):
        product_doc = ProductDocument(
            meta={"id": product.get("id")},
            id=product.get("id"),
            name=product.get("name"),
            description=product.get("description"),
            thumbnail=product.get("thumbnail"),
            price=product.get("price"),
            hot_price=product.get("hot_price"),
            category_id=product.get("category_id"),
            created_at=product.get("created_at"),
        )
        return product_doc.save()

    @staticmethod
    @shared_task
    def delete(pk):
        try:
            product_doc = ProductDocument.get(id=str(pk))
            return product_doc.delete()
        except NotFoundError:
            # Xử lý trường hợp không tìm thấy tài liệu để xóa
            return {"error": "Document not found"}

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):
        search = ProductDocument.search()

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
        order_by = query_params.get("order_by", "_score")
        order_type = query_params.get("order_type", "desc")
        page_size = query_params.get("page_size", 10)
        page = query_params.get("page", 1)
        skip = (page - 1) * page_size  # Tính toán skip từ page và page_size

        # Xử lý trường hợp is_deleted
        if is_deleted is not None:
            query = (
                Exists(field="deleted_at")
                if is_deleted
                else ~Exists(field="deleted_at")
            )
            search = search.query(query)

            if delete_from:
                search = search.query(Range(deleted_at={"gte": delete_from}))
            if delete_to:
                search = search.query(Range(deleted_at={"lte": delete_to}))
        else:
            search = search.filter("bool", must_not=Exists(field="deleted_at"))

        # Lọc theo các thuộc tính khác
        if keyword:
            search = search.query(
                MultiMatch(
                    query=keyword,
                    fields=["name", "description"],
                    fuzziness="AUTO",
                )
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
                        Range(hot_price={"lte": price_to}),
                        Bool(
                            must_not=Exists(field="hot_price"),
                            filter=Range(price={"lte": price_to}),
                        ),
                    ],
                    minimum_should_match=1,
                )
            )

        # Xử lý phân trang
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

        products = [product for product in response.hits]

        if paginate:
            return {
                "page_count": (response.hits.total.value - 1) // page_size + 1,
                "item_count": response.hits.total.value,
                "page_size": page_size,
                "page": page,
                "data": products,
            }

        return products
