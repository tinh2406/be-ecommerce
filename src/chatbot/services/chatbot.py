import json

from src.chatbot.constants import NavigateCommand

from ..prompt import (
    GET_COMPARE_PRODUCT_PARAMS_PROMPT,
    GET_DETAIL_PRODUCT_PARAMS_PROMPT,
    GET_NAVIGATION_TYPE_PROMPT,
    GET_SEARCH_PRODUCT_PARAMS_PROMPT,
    GET_TYPE_ACTION_PROMPT,
)
from ..utils import retrieve_categories, retrieve_products
from .LLM import LLM
from .vector_db import search_categories, search_other, search_products

categories = retrieve_categories()
products = retrieve_products()


class ChatbotService:

    @classmethod
    def generate_response(cls, histories, question):
        try:
            response = LLM.retrieve_user_question_with_history(histories)
            question = ChatbotService.extract_json_response(response)["question"]
            print(question)

            response = LLM.retrieve_what_user_wants(question)
            actions = ChatbotService.extract_json_response(response)
            print(actions)

            responses = []
            navigates = []
            _actions = []
            is_contact_support = False
            for action in actions:
                type_question = action["type_question"]
                if type_question == "search_products":
                    response = ChatbotService.list_product_actions(action["content"])
                    navigates.append(
                        {
                            "params": response,
                            "url": NavigateCommand.NAVIGATE_ADDRESSES[
                                NavigateCommand.GO_TO_HOME
                            ],
                        }
                    )
                elif type_question == "compare_products":
                    response = ChatbotService.compare_products_actions(
                        action["content"]
                    )
                    responses.append(
                        {"products": response, "question": action["content"]}
                    )
                elif type_question == "navigate_to_product_detail":
                    response = ChatbotService.get_detail_product_actions(
                        action["content"]
                    )
                    navigates.append(
                        {
                            "product_id": response,
                            "url": NavigateCommand.NAVIGATE_ADDRESSES[
                                NavigateCommand.GO_TO_PRODUCT_DETAILS
                            ],
                        }
                    )
                elif type_question == "question_product":
                    response = ChatbotService.question_detail_product_actions(
                        action["content"]
                    )
                    responses.append(
                        {"product": response, "question": action["content"]}
                    )

                elif type_question == "question_category":
                    response = ChatbotService.retrieve_category_actions(
                        action["content"]
                    )
                    responses.append({"data": response, "question": action["content"]})

                elif type_question == "navigate_to_others_page":
                    response = ChatbotService.navigate_actions(action["content"])
                    navigates.append(
                        {"url": NavigateCommand.NAVIGATE_ADDRESSES[response.get("url")]}
                    )
                elif type_question == "action":
                    response = ChatbotService.get_actions_actions(action["content"])
                    actions.append(
                        {
                            "action": response["action"],
                            "product_id": response["product_id"],
                        }
                    )
                elif type_question == "contact_support":
                    is_contact_support = True
                elif type_question == "unknown":
                    response = cls.unknow_handle(action["content"])

                    if response and response.get("metadata"):
                        metadata = response["metadata"]
                        if metadata.get("url"):
                            navigates.append({"url": metadata["url"]})
                        else:
                            responses.append(
                                {"data": response, "question": action["content"]}
                            )

            print(responses, navigates, _actions, is_contact_support)

            response = ""
            if len(responses) > 0:
                response += LLM.retrieve_answer(responses)
            if len(navigates) > 0:
                navigated = LLM.get_navigated_success(question)
                if len(responses) > 0:
                    response += f" Đồng thời {navigated}"
                else:
                    response += f" {navigated} "
            if len(_actions) > 0:
                if len(responses) > 0:
                    response += " Đồng thời tôi đã thực hiện hành động bạn yêu cầu. "
                else:
                    response += " Tôi đã thực hiện hành động bạn yêu cầu. "
            if is_contact_support:
                if len(responses) > 0:
                    response += (
                        " Đồng thời tôi đã chuyển thông tin đến bộ phận hỗ trợ. "
                    )
                else:
                    response += " Tôi đã chuyển thông tin đến bộ phận hỗ trợ. "

            return response, navigates, _actions, is_contact_support
        except Exception as e:
            print("Error", e)

        try:
            responses = []
            navigates = []

            response = cls.unknow_handle(action["content"])

            if response and response.get("metadata"):
                metadata = response["metadata"]
                if metadata.get("url"):
                    navigates.append({"url": metadata["url"]})
                else:
                    responses.append({"data": response, "question": action["content"]})

            response = ""
            if len(responses) > 0:
                response += LLM.retrieve_answer(responses)
            if len(navigates) > 0:
                navigated = LLM.get_navigated_success(question)
                if len(responses) > 0:
                    response += f" Đồng thời {navigated}"
                else:
                    response += f" {navigated} "

            return response, navigates, [], False
        except Exception:

            response = LLM.retrieve_error_response(question)
            print(response)
            return response, [], [], False

    @classmethod
    def list_product_actions(cls, question):

        system_prompt = GET_SEARCH_PRODUCT_PARAMS_PROMPT

        response = LLM.extract_user_question_info(question, system_prompt)
        response_dict = cls.extract_json_response(response)
        category = response_dict.get("category")

        if category:
            category = category.lower()
            cats = []
            while len(cats) < 3:
                for cat in categories:
                    if category in cat["name"].lower():
                        cats.append(cat["id"])
                break
            if cats:
                response_dict["category"] = cats

        return response_dict

    @classmethod
    def compare_products_actions(cls, question):
        compare_prompt = GET_COMPARE_PRODUCT_PARAMS_PROMPT

        response = LLM.extract_user_question_info(question, compare_prompt)
        response_dict = cls.extract_json_response(response)

        product_ids = response_dict.get("product_ids") or []
        urls = response_dict.get("urls") or []
        product_names = response_dict.get("product_names") or []

        for url in urls:
            product_id = url.split("/")[-1]
            product_ids.append(product_id)
        for product_name in product_names:
            for product in products:
                if product_name.lower() in product["name"].lower():
                    product_ids.append(product["id"])
                    break

        if len(set(product_ids)) < 2:
            return {"error": "Cần ít nhất 2 sản phẩm để so sánh"}

        _products = []
        for product in products:
            if product["id"] in product_ids:
                _products.append(product)

        if len(_products) < 2:
            return {"error": "Cần ít nhất 2 sản phẩm để so sánh"}

        return _products

    @classmethod
    def retrieve_category_actions(cls, question):
        shoted_question = LLM.shoten_question(question)
        response = search_categories(shoted_question)
        response = LLM.retrieve_from_vector_response(question, response)
        return cls.extract_json_response(response)

    @classmethod
    def get_detail_product_actions(cls, question):
        detail_prompt = GET_DETAIL_PRODUCT_PARAMS_PROMPT

        response = LLM.extract_user_question_info(question, detail_prompt)
        response_dict = cls.extract_json_response(response)

        product_id = response_dict.get("product_id")
        url = response_dict.get("url")
        name = response_dict.get("name")
        if url:
            product_id = url.split("/")[-1]
        if name:
            for product in products:
                if name.lower() == product["name"].lower():
                    product_id = product["id"]
                    break

        if not product_id:
            return "Không tìm thấy sản phẩm phù hợp"

        for product in products:
            if product["id"] == product_id.replace("-", ""):
                return product_id

        return "Không tìm thấy sản phẩm phù hợp"

    @classmethod
    def question_detail_product_actions(cls, question):
        question.replace("-", "")

        try:
            detail_prompt = GET_DETAIL_PRODUCT_PARAMS_PROMPT

            response = LLM.extract_user_question_info(question, detail_prompt)
            response_dict = cls.extract_json_response(response)

            product_id = response_dict.get("product_id")
            url = response_dict.get("url")
            name = response_dict.get("name")
            if url:
                product_id = url.split("/")[-1]
            if name:
                for product in products:
                    if name.lower() == product["name"].lower():
                        product_id = product["id"]
                        break

                for product in products:
                    if product["id"] == product_id.replace("-", ""):
                        return product

            for product in products:
                if product["id"] == product_id.replace("-", ""):
                    description = product["description"]
                    description = description[: min(1000, len(description))]
                    product["description"] = description
                    return product

        except Exception:
            pass

        shoted_question = LLM.shoten_question(question)
        response = search_products(shoted_question)
        response = LLM.retrieve_from_vector_response(question, response)
        return cls.extract_json_response(response)

    @classmethod
    def navigate_actions(cls, question):
        navigate_prompt = GET_NAVIGATION_TYPE_PROMPT

        response = LLM.extract_user_question_info(question, navigate_prompt)
        response_dict = ChatbotService.extract_json_response(response)

        url = NavigateCommand.NAVIGATE_ADDRESSES.get(response_dict.get("type"))
        if url:
            return str({"url": url})
        return "Xin lỗi, tôi không thể xác định yêu cầu của bạn"

    @classmethod
    def get_actions_actions(cls, question):
        detail_prompt = GET_TYPE_ACTION_PROMPT

        response = LLM.extract_user_question_info(question, detail_prompt)
        response_dict = cls.extract_json_response(response)

        product_id = response_dict.get("product_id")
        url = response_dict.get("url")
        product_name = response_dict.get("product_name")
        if url:
            product_id = url.split("/")[-1]
        if product_name:
            for product in products:
                if product_name.lower() in product["name"].lower():
                    product_id = product["id"]
                    break

        if not product_id:
            return "Không tìm thấy sản phẩm phù hợp"

        action = response_dict.get("action")
        if action not in ["add_to_cart", "add_to_wishlist"]:
            return "Xin lỗi, tôi không thể xác định yêu cầu của bạn"

        return {"product_id": product_id, "action": action}

    @classmethod
    def gossip(cls, question):
        response = LLM.retrieve_answer(question)
        return response

    @classmethod
    def unknow_handle(cls, question):
        shoted_question = LLM.shoten_question(question)
        response = search_other(shoted_question)
        response = LLM.retrieve_from_vector_response(question, response)
        return cls.extract_json_response(response)

    @classmethod
    def extract_json_response(cls, answer: str):
        try:
            return json.loads(answer)
        except Exception:
            pass

        try:
            answer = answer.split("```json")[1].split("```")[0]
            return json.loads(answer)
        except Exception:
            pass
        return {}

    @classmethod
    def generate_name_for_conversation(cls, message):
        response = LLM.generate_conversation_name(message)
        print(response)
        return cls.extract_json_response(response)["name"]
