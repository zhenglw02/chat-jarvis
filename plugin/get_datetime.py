import logging
import datetime

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class GetDatetimePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "get_datetime"

    def get_chinese_name(self):
        return "查询当前时间"

    def get_description(self):
        return "获取当前时间的接口，当我询问你关于日期、时间相关的问题时，你应该调用本接口，根据接口返回的时间信息回答我的问题。\n" \
               "当你需要操作日程时，你应该调用本接口，获取当前时间，然后根据当前时间计算出调用【管理日程接口】的正确参数。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        now = datetime.datetime.now()
        result = "今天是{}年{}月{}日{}时{}分{}秒".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
        return PluginResult.new(result=result, need_call_brain=True)
