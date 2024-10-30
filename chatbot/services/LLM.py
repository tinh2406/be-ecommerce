import json

from django.conf import settings
from openai import OpenAI

class LLM:

    def __init__(self):
        self.token = settings.GPT_TOKEN
        self.endpoint = "https://models.inference.ai.azure.com"
        self.model_name = "gpt-4o-mini"

        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )

    def get_response(self, question):
        response = self.client.chat.completions.create(
            messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": question
        }
    ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=self.model_name
        )
        answer = response.choices[0].message.content
        return json.loads(answer)


