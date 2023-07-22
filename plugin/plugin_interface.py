import logging
from abc import ABCMeta, abstractmethod
from jarvis.jarvis import Jarvis


class PluginResult(object):
    def __init__(self):
        # 字符串格式，AI主要参考的结果
        self.result = None
        # 是否需要在执行完成后再次调用大脑处理
        self.need_call_brain = None

    @staticmethod
    def new(result: str, need_call_brain: bool):
        r = PluginResult()
        r.result = result
        r.need_call_brain = need_call_brain
        return r


class AbstractPlugin(metaclass=ABCMeta):

    @abstractmethod
    def valid(self) -> bool:
        pass

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_chinese_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def get_parameters(self):
        pass

    @abstractmethod
    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        pass
