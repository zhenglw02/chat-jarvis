import logging
import openai
import tkinter as tk
import threading

from config.system_config import OPENAI_API_KEY
from modules.dashboard.dashboard_interface import AbstractDashBoard

openai.api_key = OPENAI_API_KEY


class SimpleDashboard(AbstractDashBoard):
    def __init__(self):
        self._logger = None
        self._text_entry = None
        self._user_input = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def start(self, callback):
        def wait_user_input(*args):
            # 创建主窗口
            window = tk.Tk(className="jarvis dashboard")
            window.title("贾维斯交互板")

            # 创建文本框和按钮
            self._text_entry = tk.Text(window, height=50, width=100)
            self._text_entry.pack()

            def callback_user_input():
                content = self._text_entry.get("1.0", tk.END)
                callback(content)

            submit_button = tk.Button(window, text="提交", command=callback_user_input)
            submit_button.pack()

            window.mainloop()

        threading.Thread(target=wait_user_input).start()

    def get_new_user_input(self) -> str:
        # 如果输入框里的内容没有变化，则不再返回，大概率是用户忘了清空了
        user_input = self._text_entry.get("1.0", tk.END)
        if user_input != "\n" and self._user_input != user_input:
            self._user_input = user_input
            return user_input
        else:
            return ""