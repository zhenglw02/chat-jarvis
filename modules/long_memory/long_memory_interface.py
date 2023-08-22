import logging
from abc import ABCMeta, abstractmethod


class LongMemoryItem:
    def __init__(self):
        self.content = None
        self.id = None
        self.metadata = None
        self.distance = None

    @staticmethod
    def new(content: str, id: str, metadata: dict, distance: float = None):
        item = LongMemoryItem()
        item.content = content
        item.id = id
        item.metadata = metadata
        item.distance = distance
        return item


class AbstractLongMemory(metaclass=ABCMeta):

    @abstractmethod
    def init(self, logger: logging.Logger):
        pass

    @abstractmethod
    def save(self, items: [LongMemoryItem]):
        pass

    @abstractmethod
    def search(self, text: str, n_results: int, metadata_filter: dict) -> [LongMemoryItem]:
        pass
