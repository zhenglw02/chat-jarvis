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
        return "获取当前时间的接口，当我问你关于我的日程相关的内容时，你应该调用本接口。\n" \
               "当我询问你关于日期、时间相关的问题时，你应该调用本接口，根据接口返回的时间信息回答我的问题。\n" \
               "当你需要【操作日程】时，你应该调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        now = datetime.datetime.now()
        weekday = now.date().weekday()
        weekday_chinese_map = {
            0: "星期一",
            1: "星期二",
            2: "星期三",
            3: "星期四",
            4: "星期五",
            5: "星期六",
            6: "星期日",
        }
        result = "现在是{}年{}月{}日{}时{}分{}秒，{}".format(now.year, now.month, now.day, now.hour, now.minute,
                                                          now.second, weekday_chinese_map.get(weekday))
        return PluginResult.new(result=result, need_call_brain=True)
