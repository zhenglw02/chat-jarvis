import logging
from abc import ABCMeta, abstractmethod

from modules.memory.memory_interface import AbstractMemory
from modules.model.chat_item import ChatItem


class AbstractBrain(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger, functions: list, memory: AbstractMemory):
        pass

    @abstractmethod
    def handle_request(self, chat_item: ChatItem, result_callback: callable):
        pass
