from elasticsearch_dsl import Date, Document, Keyword, Text


class ProductDocument(Document):

    class Index:
        name = "products"

    id = Keyword()
    name = Text()
    description = Text()
    price = Keyword()
    thumbnail = Text()
    hot_price = Keyword()

    category_id = Keyword()
    created_at = Date()
    deleted_at = Date()
