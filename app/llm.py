from langchain_openai import ChatOpenAI
from typing import List
from app.config import llm


class LLM():

    def __init__(self):
        print('LLM => START')
        pass
    
    def config(self, type: str):
        if not type:
            raise ValueError("type is empty")
        
        if (type == 'qwen'):
            return ChatOpenAI(
                openai_api_key=llm.get("api_key"),
                openai_api_base=llm.get("api_base"),
                model_name=llm.get("model_name"),
                request_timeout=10,
                streaming=True
            )

    def ask(self):
        print('selected ask llm')
        return self.config('qwen')

    def ask_tools(self, tools: List):
        print('selected ask tools llm')
        return self.config('qwen').bind_tools(tools)