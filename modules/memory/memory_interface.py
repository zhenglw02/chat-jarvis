import logging
from abc import ABCMeta, abstractmethod
from modules.model.chat_item import ChatItem
from modules.long_memory.long_memory_interface import AbstractLongMemory


class AbstractMemory(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger, long_memory: AbstractLongMemory):
        pass

    @abstractmethod
    def save(self, message: ChatItem):
        pass

    @abstractmethod
    def load_recent(self):
        pass

    @abstractmethod
    def clear_recent(self):
        pass
