from app.prompts import SCENE_PROMPT, PHOTO_PROMPT
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List, Dict, Any
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from dashscope import ImageSynthesis

import requests

from app.config import llm as _llm
from app.types import VideoScript
from app.llm import LLM

import json

llm = LLM()


class State(TypedDict):
    input: str
    videoscript: List[VideoScript]


class LLMNodeGraph():

    def __init__(self):

        print('Graph => START')

        self.graph = None
        self.graph_builder = StateGraph(state_schema=State)
    

    def chatbot(self):

        self.graph_builder.add_node('generate_scene', RunnableLambda(self.generate_scene))
        self.graph_builder.add_node('generate_photo', RunnableLambda(self.generate_photo))

        self.graph_builder.add_edge(START, 'generate_scene')
        self.graph_builder.add_edge('generate_scene', 'generate_photo')
        self.graph_builder.add_edge('generate_photo', END)

        self.graph = self.graph_builder.compile()
        return self.graph

    
    def generate_scene(self, state: State):

        chat = llm.ask()

        result = chat.invoke([
            { "role": 'system', "content": SCENE_PROMPT },
            { "role": "user", "content": state['input'] }
        ])
        
        content = result.content

        
        try:
            videoscript = json.loads(content)
        except json.JSONDecodeError:
            # 处理异常或返回空结构
            videoscript = []
        return {"videoscript": videoscript}

    def generate_photo(self, state: State):

        previous_prompt = ''
        for scene in state['videoscript']['scenes']:
            prompt = PHOTO_PROMPT.format(
                current_scene=scene,
                previous_frame_description=previous_prompt,
            )
            print(prompt)
            chat = llm.ask()

            result = chat.invoke(prompt)
            previous_prompt = result.content

            rsp = ImageSynthesis.call(
                api_key=_llm.get('api_key'),
                model="wanx2.1-t2i-turbo",
                prompt=result.content,  # 传单个字符串的列表或直接传字符串，根据接口要求
                n=4,
                # seed=2025810,
                size='1024*1024'
            )

            if rsp.status_code == HTTPStatus.OK:
                for result in rsp.output.results:
                    file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                    with open('./%s' % file_name, 'wb+') as f:
                        f.write(requests.get(result.url).content)
            else:
                print(f"Failed for prompt: {prompt}, status_code: {rsp.status_code}")


            
        # chat = llm.ask()
        # #  current_scene=scene,
        # # previous_frame_description=previous_prompt
        # result = chat.invoke(PHOTO_PROMPT.format(current_scene=state['videoscript']))
        
        # try:
        #     photos = json.loads( result.content)
        # except json.JSONDecodeError:
        #     # 处理异常或返回空结构
        #     photos = []

        # previous_prompt = ""

        # for prompt in photos:
        #     p = 
        #     rsp = ImageSynthesis.call(
        #         api_key=_llm.get('api_key'),
        #         model="wan2.2-t2i-flash",
        #         prompt=prompt.get('prompt'),  # 传单个字符串的列表或直接传字符串，根据接口要求
        #         n=1,
        #         seed=2025810,
        #         size='1024*1024'
        #     )

        #     if rsp.status_code == HTTPStatus.OK:
        #         for result in rsp.output.results:
        #             file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        #             with open('./%s' % file_name, 'wb+') as f:
        #                 f.write(requests.get(result.url).content)
        #     else:
        #         print(f"Failed for prompt: {prompt}, status_code: {rsp.status_code}")

        

