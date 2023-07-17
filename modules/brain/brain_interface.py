import logging
from abc import ABCMeta, abstractmethod

from modules.memory.memory_interface import AbstractMemory


class AbstractBrain(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger, functions, memory: AbstractMemory):
        pass

    @abstractmethod
    def handle_request(self, message, message_callback):
        pass
