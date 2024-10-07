from elasticsearch_dsl import Date, Document, Integer, Text


class UserDocument(Document):

    class Index:
        name = "users"

    id = Text()
    name = Text()
    email = Text()
    role = Integer()
    birthday = Date()
    phone = Text()
    gender = Integer()
    deleted_at = Date()
    banned_at = Date()
    created_at = Date()
