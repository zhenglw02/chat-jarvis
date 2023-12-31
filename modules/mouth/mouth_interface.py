import logging
from abc import ABCMeta, abstractmethod


class AbstractMouth(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def speak(self, content: str, finish_callback: callable):
        pass

    @abstractmethod
    def shutup(self):
        pass

    @abstractmethod
    def wait_speak_finish(self):
        pass
