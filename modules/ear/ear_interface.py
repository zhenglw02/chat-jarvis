import logging
from abc import ABCMeta, abstractmethod


class AbstractEar(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def start(self, callback: callable):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def go_on(self):
        pass

    @abstractmethod
    def sleep(self):
        pass
