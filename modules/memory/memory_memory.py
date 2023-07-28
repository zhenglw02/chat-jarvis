import logging

from config import system_config
from modules.memory.memory_interface import AbstractMemory


class MemoryMemory(AbstractMemory):
    def __init__(self):
        self._logger = None
        self._messages = None
        self._system_prompt = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._messages = []

    def save(self, message):
        self._messages.append(message)
        if len(self._messages) == 1:
            self._system_prompt = message
        if len(self._messages) > system_config.MEMORY_MAX_LENGTH:
            self._logger.debug("memory is max, clean")
            _new_messages = [self._system_prompt]
            for message in self._messages[1 - system_config.MEMORY_MAX_LENGTH:]:
                _new_messages.append(message)
            self._messages = _new_messages

    def load_recent(self):
        return self._messages

    def clear_recent(self):
        self._messages = self._messages[:1]
