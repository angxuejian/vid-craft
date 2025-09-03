# from app.prompts import SCENE_PROMPT, PHOTO_PROMPT
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List, Dict, Any
from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from dashscope import ImageSynthesis
import dashscope
from dashscope import MultiModalConversation
from dashscope import VideoSynthesis
import mimetypes

import requests

from app.config import llm as _llm
from app.types import VideoScript
from app.llm import LLM

import json

llm = LLM()


class State(TypedDict):
    input: str
    sketch: str
    # videoscript: List[VideoScript]


class LLMNodeGraph():

    def __init__(self):

        self.graph = None
        self.graph_builder = StateGraph(state_schema=State)

    def builder_node(self): 
        # self.graph_builder.add_node('generate_sketch', RunnableLambda(self.generate_sketch))
        # self.graph_builder.add_node('generate_anime_img', RunnableLambda(self.generate_anime_img))
        self.graph_builder.add_node('generate_anime_video', RunnableLambda(self.generate_anime_video))

        self.graph_builder.add_edge(START, 'generate_anime_video')
        # self.graph_builder.add_edge('generate_sketch', 'generate_anime_img')
        self.graph_builder.add_edge('generate_anime_video', END)

        self.graph = self.graph_builder.compile()
        return self.graph
        
    def generate_sketch(self, state: State):
        prompt = f"""       
            请生成一幅手绘草图，风格要求：仅保留黑色线条的外部轮廓，背景为纯白。 
            要求：线条简洁清晰，无填充、无阴影、无颜色，不包含任何内部细节或线条。简约，不需要细节！
            图像格式：JPG、JPEG、PNG、TIFF 或 WEBP。  
            图像分辨率：不小于 512×512 像素，不超过 1024×1024 像素。  
            绘制的主体是：{state['input']}。
        """ 
        rsp = ImageSynthesis.call(
            api_key="",
            model="qwen-image",
            prompt=prompt,
            n=1,
            size='1328*1328'
        )

        image_url = ''

        if rsp.status_code == HTTPStatus.OK:
            # 在当前目录下保存图片
            for result in rsp.output.results:
                file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                image_url = file_name
                with open('./%s' % file_name, 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('同步调用失败, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))

        return { 'sketch': image_url }
        

    def generate_anime_img(self, state: State): 


        rsp = ImageSynthesis.call(
            api_key="",
            model='wanx-sketch-to-image-lite',
            prompt=state['input'],
            n=1,
            style='<auto>',
            sketch_image_url='https://i-blog.csdnimg.cn/direct/83e10046791e4d87a00d6f1b1cbd3ab8.png#pic_center',
            task='image2image'
        )

        print('response: %s' % rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output)
            # save file to current directory
            for result in rsp.output.results:
                file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                with open('./%s' % file_name, 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('sync_call Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))


    def generate_anime_video(self, state: State): 
        rsp = VideoSynthesis.call(
            api_key='',
            model="wanx2.1-kf2v-plus",
            # prompt="写实风格，风格清新可爱，线条流畅，色彩鲜明饱满，带有典型的日系动漫质感和阴影，背景简洁或透明",
            first_frame_url='https://i-blog.csdnimg.cn/direct/b3704c6ade064372ac83008ac59016a7.jpeg#pic_center',
            # last_frame_url='https://i-blog.csdnimg.cn/direct/6e53630a59f04f3c8ed80b447a8b869e.png#pic_center',
            resolution="720P",
            template='solaron'
        )
        print(rsp)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output.video_url)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))