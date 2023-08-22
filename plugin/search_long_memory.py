import logging
import time

from plugin.plugin_interface import AbstractPlugin, PluginResult
from modules.long_memory.long_memory_interface import LongMemoryItem
from jarvis.jarvis import Jarvis


class SearchLongMemoryPlugin(AbstractPlugin):
    def valid(self) -> bool:
        # 功能不成熟，先不开放
        return False

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "search_long_memory"

    def get_chinese_name(self):
        return "搜索长期记忆"

    def get_description(self):
        return "搜索长期记忆的接口。长期记忆内容是用户需要你长期记住的内容。\n" \
               "当对话中涉及用户个人信息，包括但不限于：用户的姓名、性别、年龄、住址、兴趣爱好、亲人朋友的上述信息，且对话上文中没有相关信息时，你应该调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "search_text": {
                    "type": "string",
                    "description": "需要搜索的关键短语。你应该把需要搜索的内容格式化一遍，再传入本字段中。以下是几个示例：\n"
                                   "【需要搜索的内容】：我叫什么？\n"
                                   "【传入的参数值】：用户的名字\n"
                                   "【需要搜索的内容】：你知道小李吗？\n"
                                   "【传入的参数值】：小李\n"
                                   "【需要搜索的内容】：我喜欢什么颜色？\n"
                                   "【传入的参数值】：用户喜欢的颜色\n",
                }
            },
            "required": ["search_text"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        results = jarvis.long_memory.search(text=args.get("search_text"), n_results=3)
        filtered_result = []
        for result in results:
            if result.distance < 0.3:
                filtered_result.append(result)

        if len(filtered_result) == 0:
            return PluginResult.new(result="长期记忆中没有相关内容。", need_call_brain=True)

        result_text = "从长期记忆中搜索到以下内容：\n"
        for r in filtered_result:
            result_text += r.content + "\n"
        return PluginResult.new(result=result_text, need_call_brain=True)
