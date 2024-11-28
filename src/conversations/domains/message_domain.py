import threading
from time import sleep

from chatbot.services.chatbot import ChatbotService
from conversations.constants import MessageRoles
from conversations.services import ConversationService, MessageService, UnReadService
from core.domains import BaseRetrieveDomain


class MessageDomain(
    BaseRetrieveDomain,
):
    main_service = MessageService

    @classmethod
    def create(cls, conversation_id, sender_id, **validated_message):
        conversation = ConversationService.get(conversation_id, raise_exception=False)
        if not conversation:
            conversation = ConversationService.create(
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

        message = MessageService.create(
            conversation=conversation, sender_id=sender_id, **validated_message
        )

        ConversationService.update_last_message(
            conversation.id, {"last_message_id": message.id}
        )

        if message.role == MessageRoles.USER:

            thread = threading.Thread(
                target=cls.create_bot_message,
                args=(conversation.id, message.content),
            )
            thread.start()
        else:
            UnReadService.add_unread(conversation_id, sender_id)
            MessageService.create_notify(sender_id, conversation.id, message.id)

        return message

    @classmethod
    def update_conversation_name(cls, conversation_id, message):
        conversation = ConversationService.get(conversation_id)
        sleep(5)
        name = ChatbotService.generate_name_for_conversation(message)

        ConversationService.update(conversation, {"name": name})
        ConversationService.conversation_name_change_notify(
            conversation.sender_id, conversation.id
        )
        return conversation

    @classmethod
    def create_bot_message(cls, conversation_id, question):

        conversation = ConversationService.get(conversation_id)

        histories = MessageService.search(
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

        message = MessageService.create_bot_message(
            conversation, response, is_contact_support, navigates, actions
        )

        UnReadService.add_unread(conversation_id, conversation.sender_id)
        ConversationService.update_last_message(
            conversation_id, {"last_message_id": message.id}
        )
        MessageService.create_notify(
            conversation.sender_id, conversation.id, message.id
        )

    @classmethod
    def update(cls, message, validated_message):
        message = MessageService.update(message, validated_message)
        return message

    @classmethod
    def search(cls, query_params):
        return MessageService.search(query_params)
