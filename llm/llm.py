from openai import OpenAI
import os


class LLMEngine():
    
    def __init__(self):
        self.__CLIENT = OpenAI()
        self.__MODEL = os.getenv('OPENAI_MODEL')

        if self.__MODEL is None:
            raise Exception("Trouble getting client or model selection")

    def get_llm_response(self, input: str):
        completion = self.__CLIENT.chat.completions.create(
            model=self.__MODEL,
            messages=[
                {'role': 'user', 'content': input}
            ]
        )
        return completion.choices[0].message.content

