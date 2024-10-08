from celery import shared_task
from django.utils import timezone
from elasticsearch_dsl.query import Exists, Range, Term

from users.document import UserDocument


class ESUserService:

    @staticmethod
    @shared_task
    def index(user: dict):
        user_doc = UserDocument(
            meta={"id": user.get("id")},
            id=user.get("id"),
            name=user.get("name"),
            email=user.get("email"),
            role=user.get("role"),
            created_at=user.get("created_at"),
        )
        return user_doc.save()

    @staticmethod
    @shared_task
    def update(user: dict):
        user_doc = UserDocument.get(id=user.get("id"))
        user_doc.update(
            name=user.get("name"),
            email=user.get("email"),
            role=user.get("role"),
            created_at=user.get("created_at"),
            deleted_at=user.get("deleted_at"),
            banned_at=user.get("banned_at"),
            birthday=user.get("birthday"),
            phone=user.get("phone"),
            gender=user.get("gender"),
        )
        return user_doc.save()

    @staticmethod
    @shared_task
    def delete(pk):
        user_doc = UserDocument.get(id=pk)
        user_doc.update(deleted_at=timezone.now())

    @classmethod
    @shared_task
    def restore(cls, pk):
        user_doc = UserDocument.get(id=pk)
        user_doc.update(deleted_at=None)

    @classmethod
    def search(cls, query_params: dict, paginate=True, **kwargs):

        search = UserDocument.search()

        # Lấy các tham số truy vấn
        keyword = query_params.get("keyword")
        role = query_params.get("role")
        gender = query_params.get("gender")
        birthday = query_params.get("birthday")
        birthday_from = query_params.get("birthday_from")
        birthday_to = query_params.get("birthday_to")
        is_all = query_params.get("is_all")
        is_deleted = query_params.get("is_deleted")
        is_banned = query_params.get("is_banned")
        created_from = query_params.get("created_from")
        created_to = query_params.get("created_to")
        delete_from = query_params.get("delete_from")
        delete_to = query_params.get("delete_to")
        banned_from = query_params.get("banned_from")
        banned_to = query_params.get("banned_to")
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

        if is_all:
            if is_deleted is not None:
                if is_deleted:
                    query = Exists(field="deleted_at")
                else:
                    query = ~Exists(field="deleted_at")
                search = search.query(query)
            if is_banned is not None:
                if is_banned:
                    query = Exists(field="banned_at")
                else:
                    query = ~Exists(field="banned_at")
                search = search.query(query)
            if delete_from:
                search = search.query(Range(deleted_at={"gte": delete_from}))
            if delete_to:
                search = search.query(Range(deleted_at={"lte": delete_to}))
            if banned_from:
                search = search.query(Range(banned_at={"gte": banned_from}))
            if banned_to:
                search = search.query(Range(banned_at={"lte": banned_to}))
        else:
            # Lọc những bản ghi không bị xóa hoặc banned
            search = search.filter(
                "bool",
                must_not=[
                    {"exists": {"field": "deleted_at"}},
                    {"exists": {"field": "banned_at"}},
                ],
            )

        # Lọc theo các thuộc tính khác
        if keyword:
            search = search.query(
                "multi_match",
                query=keyword,
                fields=["name", "email", "phone"],
                fuzziness="AUTO",
            )
        if role:
            search = search.query(Term(role=role))
        if birthday:
            search = search.query(Term(birthday=birthday))
        if birthday_from:
            search = search.query(Range(birthday={"gte": birthday_from}))
        if birthday_to:
            search = search.query(Range(birthday={"lte": birthday_to}))
        if gender:
            search = search.query(Term(gender=gender))
        if created_from:
            search = search.query(Range(created_at={"gte": created_from}))
        if created_to:
            search = search.query(Range(created_at={"lte": created_to}))

        if paginate:
            search = search.sort({order_by: {"order": order_type}})
            search = search[skip : skip + page_size]

        response = search.execute()

        users = [user for user in response.hits]

        if paginate:
            return {
                "page_count": (response.hits.total.value - 1) // page_size + 1,
                "item_count": response.hits.total.value,
                "page_size": page_size,
                "page": page,
                "data": users,
            }

        return users
