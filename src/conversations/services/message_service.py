import threading
from time import sleep

from chatbot.services.chatbot import ChatbotService
from conversations.constants import MessageRoles
from conversations.domains import ConversationDomain, MessageDomain, UnReadDomain
from core.services import BaseRetrieveService


class MessageService(
    BaseRetrieveService,
):
    main_domain = MessageDomain

    @classmethod
    def create(cls, conversation_id, sender_id, **validated_message):
        conversation = ConversationDomain.get(conversation_id, raise_exception=False)
        if not conversation:
            conversation = ConversationDomain.create(
                validated={
                    "name": "New conversation",
                    "sender_id": sender_id,
                }
            )
            cv_thread = threading.Thread(
                target=cls.update_conversation_name,
                args=(conversation.id, validated_message.get("content")),
            )
            cv_thread.start()

        message = MessageDomain.create(
            conversation=conversation, sender_id=sender_id, **validated_message
        )

        ConversationDomain.update_last_message(
            conversation.id, {"last_message_id": message.id}
        )

        if message.role == MessageRoles.USER:

            thread = threading.Thread(
                target=cls.create_bot_message,
                args=(conversation.id, message.content),
            )
            thread.start()
        else:
            UnReadDomain.add_unread(conversation_id, sender_id)
            MessageDomain.create_notify(sender_id, conversation.id, message.id)

        return message

    @classmethod
    def update_conversation_name(cls, conversation_id, message):
        conversation = ConversationDomain.get(conversation_id)
        sleep(5)
        name = ChatbotService.generate_name_for_conversation(message)

        ConversationDomain.update(conversation, {"name": name})
        ConversationDomain.conversation_name_change_notify(
            conversation.sender_id, conversation.id
        )
        return conversation

    @classmethod
    def create_bot_message(cls, conversation_id, question):

        conversation = ConversationDomain.get(conversation_id)

        histories = MessageDomain.search(
            {"conversation_id": conversation.id, "page_size": 10, "page": 1},
            paginate=False,
        )
        messages = [
            {"role": history.role, "content": history.content} for history in histories
        ]

        response, navigates, actions, is_contact_support = (
            ChatbotService.generate_response(messages, question)
        )
        print(response, navigates, actions, is_contact_support)

        message = MessageDomain.create_bot_message(
            conversation, response, is_contact_support, navigates, actions
        )

        UnReadDomain.add_unread(conversation_id, conversation.sender_id)
        ConversationDomain.update_last_message(
            conversation_id, {"last_message_id": message.id}
        )
        MessageDomain.create_notify(conversation.sender_id, conversation.id, message.id)

    @classmethod
    def update(cls, message, validated_message):
        message = MessageDomain.update(message, validated_message)
        return message

    @classmethod
    def search(cls, query_params):
        return MessageDomain.search(query_params)
