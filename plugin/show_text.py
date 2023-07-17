import logging
import tkinter as tk
import threading

from plugin.plugin_interface import AbstractPlugin, PluginResult


class ShowTextPlugin(AbstractPlugin):
    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "show_text"

    def get_chinese_name(self):
        return "展示文字"

    def get_description(self):
        return "展示文字接口。当你需要把文字或者代码类的内容展示给我时，你应该调用本接口。" \
               "注意：当我要求你生成代码时，你应该总是在生成完成后调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "你需要展示的内容。"
                                   "这个参数的值应该永远是前面一次函数调用返回的【完整结果】或用户输入的【完整内容】，你不能自己添加、修改或者删除任何内容。"
                                   "【注意】：展示代码生成的结果时，你应该带上代码后面的【代码描述部分】。",
                }
            },
            "required": ["content"],
        }

    def run(self, args: dict) -> PluginResult:
        def display():
            # 创建主窗口
            window = tk.Tk()

            # 设置窗口标题
            window.title("展示和编辑文字")

            # 创建用于展示和编辑文字的文本框
            display_text = tk.Text(window, height=300, width=100)
            display_text.pack()

            # 设置文本框为可编辑状态
            display_text.config(state=tk.NORMAL)

            # 设置初始文本内容
            initial_text = args.get("content")
            display_text.insert(tk.END, initial_text)

            window.mainloop()

        # 另起一个线程展示窗口，避免阻塞主流程
        threading.Thread(target=display).start()

        # 节约openai接口调用次数，展示出内容后就不调大脑了，返回调了也只会得到几句没意义的话
        return PluginResult.new(result="done", need_call_brain=False)
