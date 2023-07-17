import logging
from abc import ABCMeta, abstractmethod


class AbstractMemory(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def save(self, message):
        pass

    @abstractmethod
    def load_recent(self):
        pass

    @abstractmethod
    def clear_recent(self):
        pass
