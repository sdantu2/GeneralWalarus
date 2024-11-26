from openai import OpenAI
import os


class LLMEngine():
    
    def __init__(self):
        model = os.getenv("OPENAI_MODEL")
        
        if model is None:
            raise Exception("Trouble getting client or model selection")

        self.__CLIENT = OpenAI()
        self.__MODEL = model 
        
    def get_llm_response(self, input: str):
        completion = self.__CLIENT.chat.completions.create(
            model=self.__MODEL,
            messages=[
                {'role': 'user', 'content': input}
            ]
        )
        return completion.choices[0].message.content

