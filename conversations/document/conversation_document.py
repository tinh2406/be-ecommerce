from elasticsearch_dsl import Date, Document, Keyword, Text


class ConversationDocument(Document):

    class Index:
        name = "conversations"

    id = Keyword()
    name = Text()
    sender_id = Keyword()

    last_message_id = Keyword()
    last_message_content = Text()

    created_at = Date()
    updated_at = Date()
    deleted_at = Date()
