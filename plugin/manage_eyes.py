import logging
import time

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class ManageEyesPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "manage_eyes"

    def get_chinese_name(self):
        return "操作摄像头"

    def get_description(self):
        return "打开或关闭你的眼睛，即你所在电脑的摄像头。当用户要求你操作你的眼睛时，比如：睁开眼睛或闭上眼睛时，你应该使用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "本参数的值只能是两个枚举之一：open和close。当你需要开启眼睛时，应该传入open，当你需要关闭眼睛时，应该传入close。",
                }
            },
            "required": ["content"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        action = args['action']
        if action == "open":
            jarvis.eye.open()
            time.sleep(1) # 摄像头开启需要一段时间，如果在启动完成前读取图像信息可能会报错
            return PluginResult.new(result="已启动视觉能力", need_call_brain=True)
        elif action == "close":
            jarvis.eye.close()
            return PluginResult.new(result="已关闭视觉能力", need_call_brain=True)
        else:
            return PluginResult.new(result=f"未知的操作：{action}", need_call_brain=False)
