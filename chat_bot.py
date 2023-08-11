# coding: utf-8
# author: 罗旭维
# date: 2023-08-12
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import os
import gradio as gr

class Chatbot:
    def __init__(self, file):
        self.chain = None
        self.chat_history = []  # 用于存储聊天历史记录
        self.page_num: int = 0  # 当前PDF文件的页码
        self.count: int = 0  # 对话轮次
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.build_chain(file)

    def load_file(self, file):
        loader = PyPDFLoader(file)
        documents = loader.load()
        file_name = os.path.basename(file)
        return documents, file_name

    def __call__(self, query):
        self.count += 1
        # 处理用户的查询并生成答案
        result = self.chain({"question": query,
                        "chat_history": self.chat_history},
                       return_only_outputs=True)
        # print("result = ", result.keys())
        # 将当前的查询和生成的答案添加到聊天历史中
        self.chat_history += [(query, result["answer"])]
        # 从源文档中获取当前页的页码
        self.page_num = list(result["source_documents"][0])[1][1]["page"]
        return result["answer"]

    def build_chain(self, file):

        # 1. 判断openai key是否存在
        if not self.api_key:
            raise gr.Error("OpenAI key不存在，请上传")
        # 2. 文档预处理，提取内容、获取文件名
        documents, file_name = self.load_file(file)
        # 3. 创建embedding model，用于生成文档的embedding表示
        embedding_model = OpenAIEmbeddings(openai_api_key=self.api_key)
        # 4. 创建向量数据库，并将数据存进去
        vectorstore = FAISS.from_documents(documents=documents,
                                           embedding=embedding_model)
        # 5. 创建对话检索链
        self.chain = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(temperature=0.0, openai_api_key=self.api_key),
                                                      retriever=vectorstore.as_retriever(search_kwargs={"k":1}),
                                                      return_source_documents=True,)


