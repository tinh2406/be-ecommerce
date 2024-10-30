from chatbot.constants import QuestionCommand
from chatbot.prompt import CLASSIFIER_QUESTION_PROMPT, GET_PRODUCT_LIST_PROMPT
from chatbot.services.LLM import LLM

class ChatbotService:

    llm = LLM()

    @classmethod
    def extract_question_response(cls, question):
        prompt = CLASSIFIER_QUESTION_PROMPT + question
        response = cls.llm.get_response(prompt)
        response = cls.handle_by_type(response['type'], question)
        print(response)
        return response

    @classmethod
    def handle_by_type(cls, q_type, question, **kwargs):
        if q_type==QuestionCommand.LIST_PRODUCTS:
            return cls.list_product_actions(question)
        if q_type==QuestionCommand.GET_PRODUCT_DETAIL:
            return cls.get_detail_product_actions(question)
        return cls.gossip(question)
    @classmethod
    def list_product_actions(cls, question,**kwargs):
        list_prompt = GET_PRODUCT_LIST_PROMPT + question
        response = cls.llm.get_response(list_prompt)
        print(response)
        return

    @classmethod
    def get_detail_product_actions(cls,question, **kwargs):
        print(kwargs)
        return

    @classmethod
    def introduce_summary_actions(cls,**kwargs):
        print(kwargs)
        return

    @classmethod
    def compare_products_actions(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def get_purchase_history(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def get_orders_status(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def add_to_cart(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def navigate(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def contact_support(cls, **kwargs):
        print(kwargs)
        return

    @classmethod
    def gossip(cls, question):
        return cls.llm.get_response(question)

