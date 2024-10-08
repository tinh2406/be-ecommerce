from celery import shared_task

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
