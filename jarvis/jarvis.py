import json
from json.decoder import JSONDecodeError

from modules.brain.brain_interface import ChatItem
from config import system_config


class Jarvis:
    def __init__(self):
        self.mouth = None
        self.memory = None
        self.long_memory = None
        self.brain = None
        self.ear = None
        self.eye = None
        self.dashboard = None
        self._logger = None
        self._function_map = None

    def init(self, logger, function_map):
        self._logger = logger
        self._function_map = function_map

    def start(self):
        self.mouth.speak(
            "贾维斯已启动，等待您的唤醒。",
            lambda: (self.ear.start(self.handle_ear_result)),
        )
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

        # todo: 内容改写，将语音转成的文字中可能存在的错别字、英文错词等情况改写正确

        # 暂停听力，防止听到自己说的话，又触发对话逻辑，陷入死循环
        self.ear.pause()
        # 耳朵听到的配合用户手写输入的，能更方便用户使用贾维斯
        user_input = self.dashboard.get_new_user_input()
        if user_input != "":
            content += "\n以下是我手动输入的内容，请注意：只有当你认为你应该参考下面的内容作出回答：\n{}".format(
                user_input
            )
        # 根据用户输入，从长期记忆里搜索相关的内容，可以让贾维斯的回答更准确，或更发散
        long_memories = self.long_memory.search(
            text=content, n_results=system_config.LONG_MEMORY_SEARCH_COUNT
        )
        if (
            len(long_memories) > 0
            and long_memories[0].distance < system_config.LONG_MEMORY_FILTER_DISTANCE
        ):
            long_memory_info = ""
            for memory in long_memories:
                if memory.distance < system_config.LONG_MEMORY_FILTER_DISTANCE:
                    long_memory_info += memory.content
                    long_memory_info += "\n"
            if long_memory_info != "":
                content += "\n以下是【你的】长期记忆中的部分信息，你可以参考这些信息作出回答，但如果当前问题与记忆中的信息无关的话，请忽略记忆内容：\n{}".format(
                    long_memory_info
                )

        # 如果打开了眼睛，可以从眼睛中获取信息
        if self.eye.enabled():
            image_info = self.eye.parse_snapshot()
            if image_info is not None and image_info != "":
                content += (
                    f"\n以下是你从眼睛中获取的部分视觉信息，你可以参考这些信息作出回答：\n{image_info}\n"
                    f"请注意：只有当下面的问题与视觉信息有关时，你才能参开这些信息，否则，你应该忽略这些内容。"
                )

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
                self.mouth.wait_speak_finish()
                self.ear.go_on()
                return

        # 暂停听力，防止听到自己说的话，又触发对话逻辑，陷入死循环
        self.ear.pause()
        if content is None or content == "":
            return

        # 根据用户输入，从长期记忆里搜索相关的内容，可以让贾维斯的回答更准确，或更发散
        long_memories = self.long_memory.search(
            text=content, n_results=system_config.LONG_MEMORY_SEARCH_COUNT
        )
        if (
            len(long_memories) > 0
            and long_memories[0].distance < system_config.LONG_MEMORY_FILTER_DISTANCE
        ):
            long_memory_info = ""
            for memory in long_memories:
                if memory.distance < system_config.LONG_MEMORY_FILTER_DISTANCE:
                    long_memory_info += memory.content
                    long_memory_info += "\n"
            if long_memory_info != "":
                content += "\n以下是你的长期记忆中的部分信息，你可以参考这些信息作出回答：\n{}\n请注意：只有当下面的问题与长期记忆的内容有关时，你才能参考这些信息，否则，你应该忽略这些内容，不要向用户透露长期记忆的内容。".format(
                    long_memory_info
                )

        # 如果打开了眼睛，可以从眼睛中获取信息
        if self.eye.enabled():
            image_info = self.eye.parse_snapshot()
            if image_info is not None and image_info != "":
                content += (
                    f"\n以下是你从眼睛中获取的部分视觉信息，你可以参考这些信息作出回答：\n{image_info}\n"
                    f"请注意：只有当下面的问题与视觉信息有关时，你才能参考这些信息，否则，你应该忽略这些内容。"
                )

        user_input_chat_item = ChatItem.new("user", content)
        self.brain.handle_request(user_input_chat_item, self.handle_brain_result)

    def handle_brain_result(self, chat_item: ChatItem, finish: bool):
        """
        大脑的回调
        :param chat_item: 大脑生成的结果
        :param finish: 是否结束
        :return:
        """

        if chat_item.function_call:
            self._logger.info("function_call: {}".format(chat_item.function_call))
            self.execute_function_call(chat_item)
        else:
            # 百度的tts服务不支持空字符串，所以这里判断一下
            if len(chat_item.content) > 0:
                self.mouth.speak(
                    chat_item.content, self.ear.go_on if finish else lambda: {}
                )
            # 一般content为空时的回调，应该都是说完了，finish应该都是true，这里保险判断一下
            elif finish:
                self.mouth.wait_speak_finish()
                self.ear.go_on()

    def execute_function_call(self, assistant_chat_item: ChatItem):
        """
        处理大脑发出的函数调用的指令
        :param assistant_chat_item:
        :return:
        """
        if assistant_chat_item.function_call["name"] in self._function_map:
            function_info = self._function_map.get(
                assistant_chat_item.function_call["name"]
            )

            def handle_speak_finish():
                # 校验以下模型生成的调用参数是否合法，一般调show_text()展示代码的时候可能生成的参数不对
                try:
                    arguments = (
                        json.loads(assistant_chat_item.function_call["arguments"])
                        if assistant_chat_item.function_call["arguments"] != ""
                        else {}
                    )
                except JSONDecodeError as e:
                    self._logger.error(
                        "json loads arguments failed, arguments: {}, exception: {}".format(
                            assistant_chat_item.function_call["arguments"], e
                        )
                    )
                    self.mouth.speak(
                        "调用插件使用的参数不太对，这次先不调了。", lambda: {}
                    )
                    return

                result = function_info["function"](self, arguments)
                if result.need_call_brain:
                    function_chat_item = ChatItem.new(
                        "function",
                        result.result if result.result is not None else "",
                        name=assistant_chat_item.function_call["name"],
                    )
                    self.brain.handle_request(
                        function_chat_item, self.handle_brain_result
                    )
                else:
                    self.mouth.wait_speak_finish()
                    self.ear.go_on()

            self.mouth.speak(
                "正在{}".format(function_info["chinese_name"]), handle_speak_finish
            )
        else:
            self.mouth.speak(
                "未知的程序名称：{}".format(assistant_chat_item.function_call["name"]),
                self.ear.go_on(),
            )

    def handle_self_awake_request(self, chat_item: ChatItem):
        self.brain.handle_request(chat_item, self.handle_brain_result)
