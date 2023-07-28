import logging
import tkinter as tk

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class WaitUserInputPlugin(AbstractPlugin):
    def valid(self) -> bool:
        """
        过时的插件，被dashboard组件替代。相比于这个插件，dashboard是更好的交互方式。
        :return:
        """
        return False

    def __init__(self):
        self._logger = None
        self._user_input = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "wait_user_input"

    def get_chinese_name(self):
        return "等待输入"

    def get_description(self):
        return "等待并接收用户输入的接口，当你需要我手动输入文字内容，或者我要求你接收我手动输入的内容时，你应该调用本接口。\n" \
               "你应该调用本接口的场景举例如下：\n" \
               "我要写一段描述给你，你要......\n" \
               "接收我的输入，然后再......\n" \
               ".......，我发给你/我写给你。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        self._user_input = ""

        def get_text_and_destroy():
            self._user_input = text_entry.get("1.0", tk.END)
            window.destroy()  # 关闭窗口

        # 创建主窗口
        window = tk.Tk()

        # 创建文本框和按钮
        text_entry = tk.Text(window, height=10, width=30)
        text_entry.pack()

        submit_button = tk.Button(window, text="提交", command=get_text_and_destroy)
        submit_button.pack()

        # 运行主循环，这里可以阻塞主流程，用户不输入内容就不用继续处理了
        window.mainloop()
        return PluginResult.new(result=self._user_input, need_call_brain=True)
