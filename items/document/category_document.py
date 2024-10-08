from elasticsearch_dsl import Date, Document, Keyword, Text


class CategoryDocument(Document):

    class Index:
        name = "categories"

    id = Text()
    name = Text()
    parent_id = Keyword()

    created_at = Date()
    deleted_at = Date()
