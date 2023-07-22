import logging

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class SleepPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "sleep"

    def get_chinese_name(self):
        return "进入休眠"

    def get_description(self):
        return "停止对话，进入休眠接口。如果我告诉你：暂时不需要你了，或者你可以去忙了，或者你可以歇着去了，或者我没有在和你说话等内容，你应该调用本接口。" \
               "如果你从我的话语里明白了我想让你离开，你也应该调用本接口。注意：本接口不接收任何参数，当你调用本接口时你不应该传递任何参数进来。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        jarvis.ear.sleep()
        jarvis.memory.clear_recent()
        jarvis.mouth.speak("您可以随时唤醒我。", lambda: {})
        return PluginResult.new("", False)
