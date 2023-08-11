# coding: utf-8
# author: 罗旭维
# date: 2023-08-11

import gradio as gr
import os
import fitz #处理PDF、XPS和其他文档格式的库
from PIL import Image
from chat_bot import Chatbot

enable_box = gr.Textbox.update(value=None,
                               placeholder="填写 api key",
                               interactive=True)

disable_box = gr.Textbox.update(value=None,
                                placeholder="api key 已经被设置",
                                interactive=False,)


def set_apikey(key):
    os.environ["OPENAI_API_KEY"] = key
    return disable_box


def change_api_box():
    return enable_box

chat = None
def on_upload(file):
    global chat
    chat = Chatbot(file.name)
    doc = fitz.open(file.name)
    page = doc[0]
    pic = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    image = Image.frombytes("RGB", [pic.width, pic.height], pic.samples)
    return image

def render_file(file):
    # 打开PDF文档
    doc = fitz.open(file.name)
    # 根据页面获取当页的内容
    page = doc[chat.page_num]
    # 将页面渲染为分辨率为300 DPI的PNG图像，从默认的72DPI转换到300DPI
    picture = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
    # 从渲染的像素数据创建一个Image对象
    image = Image.frombytes("RGB", [picture.width, picture.height], picture.samples)
    # 返回渲染后的图像
    return image

def generate_response(history, query, file):
    '''答案生成'''
    # 首先，判断一下是否上传了PDF文档
    if not file:
        raise gr.Error(message="上传一个PDF文档")
    result = chat(query)
    # 将生成的回答每个字符添加到history中，用于实时显示答案字符 ， 举例说明：
    # [("你好吗?", "")]
    # [("你好吗?", "我")]
    # [("你好吗?", "我很")]
    # [("你好吗?", "我很好")]
    # [("你好吗?", "我很好，你")]
    # [("你好吗?", "我很好，你呢")]
    # [("你好吗?", "我很好，你呢？")]
    for char in result["answer"]:
        history[-1][-1] += char
        yield history, ""

def add_text(history, text:str):
    '''
    :param history: 用户聊天历史记录
    :param text: 用户的新输入
    :return: 更新后的history列表
    '''
    if not text:
        raise gr.Error("请输入文本")
    history = history + [(text, "")]
    return history

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=0.8):
            api_key = gr.Textbox(placeholder="请输入api key",
                                 show_label=False,
                                 interactive=True,
                                 container=False)
        with gr.Column(scale=0.2):
            new_api_key = gr.Button("修改api key")

    with gr.Row():
        chatbot = gr.Chatbot(value=[], elem_id="chatbot", height=600)
        show_pdf = gr.Image(label="预览", height=630)

    with gr.Row():
        with gr.Column(scale=0.6):
            txt = gr.Textbox(show_label=False, placeholder="请输入文本", container=False)

        with gr.Column(scale=0.2):
            submit_button = gr.Button("提交")

        with gr.Column(scale=0.2):
            button = gr.UploadButton("上传PDF文档", file_types=[".pdf"])

    api_key.submit(fn=set_apikey, inputs=[api_key], outputs=[api_key])
    new_api_key.click(fn=change_api_box,  outputs=[api_key])

    button.upload(fn=on_upload, inputs=[button], outputs=[show_pdf])
    # 提交text，生成回答
    submit_button.click(
        fn=add_text,
        inputs=[chatbot, txt],
        outputs=[chatbot],
        queue=True # 如果同时有多个请求，这个函数应当排队执行。
    ).success(
        fn=generate_response,
        inputs=[chatbot, txt, button],
        outputs=[chatbot, txt]
    ).success(
        fn=render_file,
        inputs=[button],
        outputs=[show_pdf]
    )


demo.queue(concurrency_count=1).launch()