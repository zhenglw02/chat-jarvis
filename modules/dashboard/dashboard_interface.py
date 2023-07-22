import logging
from abc import ABCMeta, abstractmethod


class AbstractDashBoard(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def start(self, callback):
        pass

    @abstractmethod
    def get_new_user_input(self) -> str:
        pass
