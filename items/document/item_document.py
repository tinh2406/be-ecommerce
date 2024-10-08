from elasticsearch_dsl import Date, Document, Text


class ItemDocument(Document):

    class Index:
        name = "items"

    id = Text()
    name = Text()
    describe = Text()
    price = Text()
    thumbnail = Text()
    hot_price = Text()

    category_id = Text()
    created_at = Date()
    deleted_at = Date()
