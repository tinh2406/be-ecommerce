from django.conf import settings
from openai import OpenAI


class MessageRoles:
    SYSTEM = "system"
    USER = "user"
    BOT = "assistant"


class LLM:
    token = settings.GPT_TOKEN
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "gpt-4o-mini"

    client = OpenAI(base_url=endpoint, api_key=token)

    @classmethod
    def generate_conversation_name(cls, message):
        user_messages = [
            {
                "role": "system",
                "content": """Bạn là chatbot và nhận được câu hỏi hoặc yêu cầu từ người dùng, hãy sinh ra tên
                cho cuộc hội thoại thật súc tích và liên quan đến câu hỏi hoặc yêu cầu của người dùng.
                Ví dụ:
                {
                "content": "Bạn có những sản phẩm nào?"
                "role": "user"
                }
                Trả lời
                {
                "name": "Thắc mắc về sản phẩm"
                }
                Ví dụ
                {
                "content": "Bạn có ô tô không?"
                "role": "user"
                }
                Trả lời
                {
                "name": "Tìm hiểu về ô tô"
                }""".replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            }
        ]

        response = cls.client.chat.completions.create(
            messages=user_messages,
            temperature=1,
            top_p=1,
            max_tokens=1000,
            model=cls.model_name,
        )
        return response.choices[0].message.content

    @classmethod
    def retrieve_user_question_with_history(cls, messages):
        user_messages = [
            {
                "role": "system",
                "content": """Bạn đang cần hiểu xem câu hỏi hoặc yêu cầu của người dùng, tuy nhiên người dùng
                                    lại thường xuyên đưa ra những câu hỏi hoặc yêu cầu ngắn gọn không đầy đủ ý nghĩa.
                                    Bạn hãy cố gắng dựa vào nội dung đoạn chat để hiểu rõ hơn về câu nói của người dùng.
                                    Và viết lại câu nói của người dùng một cách đầy đủ hơn mà người dùng thực sự đang muốn 
                                    nói về dưới dạng json.
                                    Lưu ý: không được phép trả lời trả lời câu hỏi người dùng mà chỉ cần trả về câu hỏi.
                                    Ví dụ:
                                    {
                                        "content": "Bạn có những sản phẩm nào?"
                                        "role": "user"
                                    }
                                    Trả lời
                                    {
                                        "question": "Bạn có những sản phẩm nào?"
                                    }
                                    Ví dụ
                                    {
                                        "content": "Bạn có ô tô không?"
                                        "role": "user"
                                    }
                                    {
                                        "content: "Có",
                                        "role": "bot"
                                    }
                                    {
                                        "content": "Cho tôi xem?"
                                        "role": "user"
                                    }
                                    Trả lời
                                    {
                                        "question": "Cho tôi xem ô tô mà bạn có?"
                                    }
                                    {
                                        "content": "Tôi muốn tìm tai nghe?"
                                        "role": "user"
                                    }
                                    Trả lời
                                    {
                                        "question": "Cho tôi xem tai nghe mà bạn có?"
                                    }
                                    """.replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            }
        ]
        for i in range(len(messages[-10:]), 0, -1):
            user_messages.append(messages[i - 1])

        response = cls.client.chat.completions.create(
            messages=user_messages,
            temperature=0.2,
            top_p=0.1,
            max_tokens=1000,
            model=cls.model_name,
        )
        return response.choices[0].message.content

    @classmethod
    def retrieve_what_user_wants(cls, question):
        user_messages = [
            {
                "role": "system",
                "content": """Bạn đang cần hiểu xem câu hỏi của người dùng, tuy nhiên người dùng
                                    lại thường xuyên đưa ra những câu hỏi là tổ hợp của nhiều hành động
                                    và yêu cầu bạn phải giải quyết. Với danh sách các hành động sau:
                                    {
                                        search_products: muốn tìm kiếm sản phẩm
                                        compare_products: muốn so sánh giữa các sản phẩm
                                        question_category: muốn hỏi về các loại hoặc các danh mục sản phẩm
                                        question_product: muốn hỏi về sản phẩm dựa trên id, tên hoặc url
                                        action: muốn chatbot thực hiện like hoặc thêm sản phẩm vào giỏ hàng
                                        navigate_to_product_detail: muốn điều hướng đến một sản phẩm
                                        navigate_to_others_page: muốn điều hướng đến một trang cụ thể khác chi tiết sản phẩm
                                        contact_support: người dùng trực tiếp yêu cầu hỗ trợ từ bộ phận chăm sóc khách hàng
                                        unknown: không rõ yêu cầu của người dùng
                                    }
                                    Bạn hãy cố gắng phân tích người dùng đang muốn gì và trả về cho tôi 1 json là danh sách
                                    các hành động và trích xuất câu hỏi ngắn gọn tương ứng với hành động đó. Nếu không thể phân
                                    loại được bất cứ hành động nào, hãy trả về type_question là unknown.
                                    Ví dụ:
                                    Câu hỏi: "Tôi muốn xem sản phẩm điện thoại giá rẻ."
                                    Trả lời
                                    [{
                                        "type_question": "search_products",
                                        "content": "Tôi muốn xem sản phẩm điện thoại giá rẻ."
                                    }]
                                    Ví dụ
                                    Câu hỏi: "So sánh giữa Iphone 13 và Samsung Galaxy S23."
                                    Trả lời
                                    [{
                                        "type_question": "compare_products",
                                        "content": "So sánh giữa Iphone 13 và Samsung Galaxy S23."
                                    }]
                                    Ví dụ
                                    Câu hỏi: "Tôi muốn xem sản phẩm ở url là https://localhost:3000/product/123 và
                                    hãy giới thiệu cho tôi sản phẩm đó."
                                    Trả lời
                                    [{
                                        "type_question": "navigate",
                                        "content": "Tôi muốn xem sản phẩm ở url là https://localhost:3000/product/123"
                                    },{
                                        "type_question": "question_product",
                                        "content": "Hãy giới thiệu cho tôi sản phẩm ở url là https://localhost:3000/product/123."
                                    }]
                                    """.replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "user", "content": question},
        ]

        response = cls.client.chat.completions.create(
            messages=user_messages,
            temperature=0.2,
            top_p=0.1,
            max_tokens=1000,
            model=cls.model_name,
        )
        return response.choices[0].message.content

    @classmethod
    def retrieve_error_response(cls, question):
        user_messages = [
            {
                "role": "system",
                "content": """Bạn đang cần trả lời câu hỏi của người dùng, tuy nhiên phần trả lời
                        xuất hiện lỗi và bạn không thể biết được đáp án nên trả lời gì. Bạn hãy sinh ra câu trả
                        lời để xin lỗi khách hàng một cách thân thiện và tự nhiên nhất""".replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "user", "content": question},
        ]

        response = cls.client.chat.completions.create(
            messages=user_messages,
            temperature=1.4,
            top_p=1.0,
            max_tokens=1000,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer

    @classmethod
    def extract_user_question_info(cls, question, system_prompt):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]

        response = cls.client.chat.completions.create(
            messages=messages,
            temperature=0.2,
            top_p=0.1,
            max_tokens=1000,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer

    @classmethod
    def shoten_question(cls, question):
        messages = [
            {
                "role": "system",
                "content": """Bạn hãy rút gọn câu hỏi người dung bằng cách giữ lại những từ khóa quan trọng nhất
                Ví dụ:
                Câu hỏi: "Tìm kiếm sản phẩm điện thoại giá rẻ."
                Trả lời: "sản phẩm điện thoại"
                """.replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "user", "content": question},
        ]
        response = cls.client.chat.completions.create(
            messages=messages,
            temperature=0.5,
            top_p=0.5,
            max_tokens=20,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer

    @classmethod
    def retrieve_from_vector_response(cls, question, info):
        messages = [
            {
                "role": "system",
                "content": """Bạn đang cần trả lời câu hỏi hoặc yêu cầu của người dùng, dưới đây bạn sẽ được cung cấp
                        danh sách số thông tin nhất định khá liên quan đến câu hỏi của người dùng, nhiệm vụ của
                        bạn phân tích thông tin nào là liên quan đến câu hỏi người dùng và trả về luôn thông tin đó.
                        Yêu cầu trả về dạng 1 thông tin liên quan nhất ở dạng json""".replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "system", "content": str(info)},
            {"role": "user", "content": question},
        ]
        response = cls.client.chat.completions.create(
            messages=messages,
            temperature=1.2,
            top_p=1.0,
            max_tokens=1000,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer

    @classmethod
    def retrieve_answer(cls, info):
        messages = [
            {
                "role": "system",
                "content": """Bạn đang là 1 chatbot và cần phải giải đáp thắc mắc của người dùng.
                Bạn sẽ được cung cấp danh sách câu hỏi và thông tin liên quan của người dùng tương ứng. Hãy trả lời câu hỏi
                dựa trên thông tin bạn được cung cấp một cách tự nhiên và chính xác nhất. Nếu không thể
                trả lời, hãy xin lỗi một cách tự nhiên và yêu cầu người dùng đặt câu hỏi khác.""".replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "system", "content": str(info)},
        ]

        response = cls.client.chat.completions.create(
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=1000,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer

    @classmethod
    def get_navigated_success(cls, question):
        messages = [
            {
                "role": "system",
                "content": """Bạn đang là 1 chatbot và cần phải giải đáp thắc mắc của người dùng.
                        Bạn sẽ được cung cấp câu hỏi hoặc yêu cầu của người dùng để đưa họ đến một hoặc vài trang
                        bạn hãy trả lời cho người dùng là đã đưa họ đến trang hoặc những trang đó một cách tự nhiên. Yêu
                        cầu chỉ cần trả lời rằng đã điều hướng thành không và không được tự ý suy diễn và trả lời
                        câu hỏi theo ý mình.""".replace(
                    "  ", ""
                ).replace(
                    "\n", ""
                ),
            },
            {"role": "user", "content": question},
        ]

        response = cls.client.chat.completions.create(
            messages=messages,
            temperature=1,
            top_p=1,
            max_tokens=1000,
            model=cls.model_name,
        )
        answer = response.choices[0].message.content
        return answer
