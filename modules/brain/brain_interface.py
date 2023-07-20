import logging
from abc import ABCMeta, abstractmethod

from modules.memory.memory_interface import AbstractMemory


class ChatItem:
    def __init__(self):
        self.role = None
        self.content = None
        self.function_call = None
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
    def init(self, logger: logging.Logger, functions, memory: AbstractMemory):
        pass

    @abstractmethod
    def handle_request(self, chat_item: ChatItem, result_callback):
        pass
