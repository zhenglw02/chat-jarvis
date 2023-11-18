import logging
from abc import ABCMeta, abstractmethod


class AbstractEye(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def enabled(self):
        pass

    @abstractmethod
    def parse_snapshot(self):
        pass
