import inspect
import pkgutil
import importlib
import plugin
import abc
import json

from json.decoder import JSONDecodeError
from plugin.plugin_interface import AbstractPlugin, PluginResult
from modules.ear.baidu_ear import BaiduEar
from modules.mouth.baidu_mouth import BaiduMouth
from modules.brain.gpt35_brain import GPT35Brain
from modules.memory.memory_memory import MemoryMemory
from modules.brain.brain_interface import ChatItem
import logging


class Jarvis:
    def __init__(self):
        self._mouth = None
        self._memory = None
        self._brain = None
        self._ear = None
        self._logger = None
        self._function_map = None

    def init(self, logger, function_map):
        self._logger = logger
        self._function_map = function_map

    def start(self):
        self._mouth.speak("贾维斯已启动，等待您的唤醒。", lambda: {})
        # _ear.start()会阻塞，所以把说启动词的逻辑放在前面。启动听力需要一点时间，所以等听完启动词后还要等一段时间才能对话。
        self._ear.start(self.handle_ear_result)

    def handle_ear_result(self, content):
        # 忽略耳朵的误触发
        if content is None or content == "":
            return
        user_voice_chat_item = ChatItem.new("user", content)
        self._brain.handle_request(user_voice_chat_item, self.handle_brain_result)

    def handle_brain_result(self, chat_item: ChatItem, finish: bool):
        # 暂停听力，防止听到自己说的话，又触发对话逻辑，陷入死循环
        self._ear.pause()

        if chat_item.function_call:
            self._logger.info("function_call: {}".format(chat_item.function_call))
            self.execute_function_call(chat_item)
            self._ear.go_on()
        else:
            if len(chat_item.content) > 0:  # 百度的tts服务不支持空字符串，所以这里判断一下
                self._mouth.speak(chat_item.content, self._ear.go_on if finish else lambda: {})
            elif finish:  # 一般content为空时的回调，应该都是说完了，finish应该都是true，这里保险判断一下
                self._ear.go_on()

    def execute_function_call(self, assistant_chat_item: ChatItem):
        if assistant_chat_item.function_call["name"] in self._function_map:
            function_info = self._function_map.get(assistant_chat_item.function_call["name"])

            def handle_speak_finish():
                # 校验以下模型生成的调用参数是否合法，一般调show_text()展示代码的时候可能生成的参数不对
                try:
                    arguments = json.loads(assistant_chat_item.function_call["arguments"])
                except JSONDecodeError as e:
                    self._mouth.speak("调用插件使用的参数不太对，这次先不调了。", lambda: {})
                    return

                result = function_info["function"](arguments)
                if result.need_call_brain:
                    function_chat_item = ChatItem.new("function", result.result if result.result is not None else "",
                                                      name=assistant_chat_item.function_call["name"])
                    self._brain.handle_request(function_chat_item, self.handle_brain_result)

            self._mouth.speak("正在{}".format(function_info["chinese_name"]), handle_speak_finish)
        else:
            self._mouth.speak("未知的程序名称：{}".format(assistant_chat_item.function_call["name"]), lambda: {})

    def sleep(self, args: dict):
        """
        停止一次多轮对话，直到用户主动通过AI的名字唤醒它
        :param args:
        :return:
        """
        self._ear.sleep()
        self._memory.clear_recent()
        self._mouth.speak("您可以随时唤醒我。", lambda: {})
        return PluginResult.new("", False)

    def clear_recent_memory(self, args: dict):
        self._memory.clear_recent()
        self._mouth.speak("已清空最近的记忆。", lambda: {})
        return PluginResult.new("", False)

    @staticmethod
    def load(logger: logging.Logger):
        jarvis = Jarvis()

        # todo: 涉及到贾维斯自身的功能插件，要在这里主动定义。修改插件的逻辑和贾维斯自身的执行逻辑耦合了，需要抽象一下
        function_map = {
            "sleep": {"chinese_name": "进入休眠", "function": jarvis.sleep},
            "clear_recent_memory": {"chinese_name": "清空记忆", "function": jarvis.clear_recent_memory},
        }
        functions = [
            {
                "name": "sleep",
                "description": "停止对话，进入休眠接口。如果我告诉你：暂时不需要你了，或者你可以去忙了，或者你可以歇着去了等内容，你应该调用本接口。"
                               "如果你从我的话语里明白了我想让你离开，你也应该调用本接口。"
                               "注意：本接口不接收任何参数，当你调用本接口时你不应该传递任何参数进来。",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "clear_recent_memory",
                "description": "清空记忆接口，当我要求你清空记忆时，你应该调用本接口。"
                               "注意：本接口不接收任何参数，当你调用本接口时你不应该传递任何参数进来。",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        ]

        # 从plugin目录下加载所有可用插件
        clz_list = []
        for importer, name, ispkg in pkgutil.walk_packages(plugin.__path__, "%s." % plugin.__name__):
            if not ispkg:
                module = importlib.import_module(name)
                temp_list = [value for (_, value) in inspect.getmembers(module) if inspect.isclass(value)]
                clz_list.extend(temp_list)
        for clz in clz_list:
            if not inspect.isabstract(clz) and not clz == abc.ABCMeta and isinstance(clz(), AbstractPlugin):
                obj = clz()
                obj.init(logger)
                function_map[obj.get_name()] = {"chinese_name": obj.get_chinese_name(), "function": obj.run}
                functions.append({
                    "name": obj.get_name(),
                    "description": obj.get_description(),
                    "parameters": obj.get_parameters()
                })

        logger.info("function_map: {}\n".format(function_map))
        logger.info("functions: {}\n".format(functions))

        jarvis.init(logger, function_map)

        jarvis._mouth = BaiduMouth()
        jarvis._mouth.init(logger)

        jarvis._ear = BaiduEar()
        jarvis._ear.init(logger)

        jarvis._memory = MemoryMemory()
        jarvis._memory.init(logger)

        jarvis._brain = GPT35Brain()
        jarvis._brain.init(logger, functions, jarvis._memory)

        return jarvis
