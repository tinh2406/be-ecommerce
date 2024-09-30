from elasticsearch_dsl import Document, Text, Date, Integer

class UserDocument(Document):

    class Index:
        name = 'users'

    name = Text()
    email = Text()
    role = Integer()
    birthday = Date()
    phone = Text()
    gender = Integer()
    deleted_at = Date()
    banned_at = Date()
    created_at = Date()

