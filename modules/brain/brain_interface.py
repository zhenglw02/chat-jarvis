import logging
from abc import ABCMeta, abstractmethod

from modules.memory.memory_interface import AbstractMemory


class ChatItem:
    def __init__(self):
        self.role = None
        self.content = None
        self.function_call = None
        # 函数调用的结果中使用该参数传递函数名
        self.name = None

    @staticmethod
    def new(role, content, function_call=None, name=None):
        item = ChatItem()
        item.role = role
        item.content = content
        item.function_call = function_call
        item.name = name
        return item


class AbstractBrain(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger, functions: list, memory: AbstractMemory):
        pass

    @abstractmethod
    def handle_request(self, chat_item: ChatItem, result_callback: callable):
        pass
