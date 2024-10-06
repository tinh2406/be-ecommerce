from elasticsearch_dsl import Document, Text, Date, Integer

class CategoryDocument(Document):

    class Index:
        name = 'categories'

    id = Text()
    name = Text()
    parent_id = Text()

    created_at = Date()
    deleted_at = Date()

