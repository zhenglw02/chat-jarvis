import logging
import time

from plugin.plugin_interface import AbstractPlugin, PluginResult
from modules.long_memory.long_memory_interface import LongMemoryItem
from jarvis.jarvis import Jarvis


class AddLongMemoryPlugin(AbstractPlugin):
    def valid(self) -> bool:
        # 功能不成熟，先不开放
        return False

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "add_long_memory"

    def get_chinese_name(self):
        return "增加长期记忆"

    def get_description(self):
        return "增加长期记忆的接口。长期记忆内容是用户需要你长期记住的内容。\n" \
               "当用户告诉你某个信息很重要，或者让你记住某个信息时，你应该调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "你需要记住的信息内容。你应该把用户告诉你的内容格式化一遍，再传入本字段中。以下是几个示例：\n"
                                   "【用户说的内容】：我叫小郑。\n"
                                   "【传入的参数值】：用户的名字是小郑。\n"
                                   "【用户说的内容】：这是我的朋友，叫小李。\n"
                                   "【传入的参数值】：用户有个朋友，叫小李。\n"
                                   "【用户说的内容】：我喜欢蓝色。\n"
                                   "【传入的参数值】：用户喜欢的颜色是蓝色。\n",
                }
            },
            "required": ["content"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        item = LongMemoryItem.new(content=args.get('content'), metadata={"add_time": time.time()},
                                  id=str(time.time_ns()))
        jarvis.long_memory.save([item])
        return PluginResult.new(result="已成功记忆：{}".format(args.get('content')), need_call_brain=True)
