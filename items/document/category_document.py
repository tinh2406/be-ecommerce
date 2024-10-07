from elasticsearch_dsl import Date, Document, Text


class CategoryDocument(Document):

    class Index:
        name = "categories"

    id = Text()
    name = Text()
    parent_id = Text()

    created_at = Date()
    deleted_at = Date()
