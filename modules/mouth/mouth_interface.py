import logging
from abc import ABCMeta, abstractmethod


class AbstractMouth(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def speak(self, content, finish_callback):
        pass
