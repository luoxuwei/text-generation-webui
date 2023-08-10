# coding: utf-8
# author: 罗旭维
# date: 2023-08-11

import gradio as gr
import os

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


demo.queue(concurrency_count=1).launch()