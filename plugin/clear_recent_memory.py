import logging

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class ClearRecentMemoryPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "clear_recent_memory"

    def get_chinese_name(self):
        return "清空记忆"

    def get_description(self):
        return "清空记忆接口，当我要求你清空记忆时，你应该调用本接口。注意：本接口不接收任何参数，当你调用本接口时你不应该传递任何参数进来。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        jarvis.memory.clear_recent()
        jarvis.mouth.speak("已清空最近的记忆。", lambda: {})
        return PluginResult.new("", False)
