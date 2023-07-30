import json
from json.decoder import JSONDecodeError

from modules.brain.brain_interface import ChatItem


class Jarvis:
    def __init__(self):
        self.mouth = None
        self.memory = None
        self.brain = None
        self.ear = None
        self.dashboard = None
        self._logger = None
        self._function_map = None

    def init(self, logger, function_map):
        self._logger = logger
        self._function_map = function_map

    def start(self):
        self.mouth.speak("贾维斯已启动，等待您的唤醒。", lambda: (self.ear.start(self.handle_ear_result)))
        self.dashboard.start(self.handle_dashboard_result)

    def handle_ear_result(self, content: str):
        """
        耳朵的回调，当听到用户说话并停止一段时间后触发
        :param content: 听到的内容
        :return:
        """
        # 忽略耳朵的误触发
        if content is None or content == "":
            return
        # 耳朵听到的配合用户手写输入的，能更方便用户使用贾维斯
        user_input = self.dashboard.get_new_user_input()
        if user_input != "":
            content += "\n以下是我手动输入的内容，请注意：只有当你认为你应该参考下面的内容作出回答：\n{}".format(
                user_input)
        user_voice_chat_item = ChatItem.new("user", content)
        self.brain.handle_request(user_voice_chat_item, self.handle_brain_result)

    def handle_dashboard_result(self, content: str, action: str):
        """
        交互板的回调，用户手动点击交互板的按钮时触发
        :param content: 用户输入的内容
        :param action: 用户点击的动作
        :return:
        """
        if action is not None and action != "":
            if action == "shutup":
                self.mouth.shutup()
                self.ear.go_on()
                return

        if content is None or content == "":
            return
        user_input_chat_item = ChatItem.new("user", content)
        self.brain.handle_request(user_input_chat_item, self.handle_brain_result)

    def handle_brain_result(self, chat_item: ChatItem, finish: bool):
        """
        大脑的回调
        :param chat_item: 大脑生成的结果
        :param finish: 是否结束
        :return:
        """
        # 暂停听力，防止听到自己说的话，又触发对话逻辑，陷入死循环
        self.ear.pause()

        if chat_item.function_call:
            self._logger.info("function_call: {}".format(chat_item.function_call))
            self.execute_function_call(chat_item)
            self.mouth.wait_speak_finish()
            self.ear.go_on()
        else:
            if len(chat_item.content) > 0:  # 百度的tts服务不支持空字符串，所以这里判断一下
                self.mouth.speak(chat_item.content, self.ear.go_on if finish else lambda: {})
            elif finish:  # 一般content为空时的回调，应该都是说完了，finish应该都是true，这里保险判断一下
                self.mouth.wait_speak_finish()
                self.ear.go_on()

    def execute_function_call(self, assistant_chat_item: ChatItem):
        """
        处理大脑发出的函数调用的指令
        :param assistant_chat_item:
        :return:
        """
        if assistant_chat_item.function_call["name"] in self._function_map:
            function_info = self._function_map.get(assistant_chat_item.function_call["name"])

            def handle_speak_finish():
                # 校验以下模型生成的调用参数是否合法，一般调show_text()展示代码的时候可能生成的参数不对
                try:
                    arguments = json.loads(assistant_chat_item.function_call["arguments"])
                except JSONDecodeError as e:
                    self._logger.error("json loads arguments failed, arguments: {}, exception: {}".format(
                        assistant_chat_item.function_call["arguments"], e))
                    self.mouth.speak("调用插件使用的参数不太对，这次先不调了。", lambda: {})
                    return

                result = function_info["function"](self, arguments)
                if result.need_call_brain:
                    function_chat_item = ChatItem.new("function", result.result if result.result is not None else "",
                                                      name=assistant_chat_item.function_call["name"])
                    self.brain.handle_request(function_chat_item, self.handle_brain_result)

            self.mouth.speak("正在{}".format(function_info["chinese_name"]), handle_speak_finish)
        else:
            self.mouth.speak("未知的程序名称：{}".format(assistant_chat_item.function_call["name"]), lambda: {})
