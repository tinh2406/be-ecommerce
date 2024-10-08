from elasticsearch_dsl import Date, Document, Keyword, Text


class ItemDocument(Document):

    class Index:
        name = "items"

    id = Keyword()
    name = Text()
    description = Text()
    price = Keyword()
    thumbnail = Text()
    hot_price = Keyword()

    category_id = Keyword()
    created_at = Date()
    deleted_at = Date()
