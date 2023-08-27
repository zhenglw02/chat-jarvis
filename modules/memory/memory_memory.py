import logging
import openai

from config import system_config
from modules.memory.memory_interface import AbstractMemory
from modules.model.chat_item import ChatItem

openai.api_key = system_config.MEMORY_SUMMARY_OPENAI_API_KEY
openai.api_base = system_config.MEMORY_SUMMARY_OPENAIAPI_BASE


class MemoryMemory(AbstractMemory):
    def __init__(self):
        self._logger = None
        self._messages = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._messages = []

    def save(self, message: ChatItem):
        self._messages.append(message)
        if len(self._messages) > system_config.MEMORY_MAX_LENGTH:
            self._logger.debug("memory is max, summary them")
            _new_messages = []
            if system_config.MEMORY_SUMMARY_ENABLE:
                history = ""
                for message in self._messages[1:]:
                    history += "【{}】：{}\n".format(message.role, message.content)
                response = openai.ChatCompletion.create(
                    model=system_config.MEMORY_SUMMARY_OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个资深的文字工作者."},
                        {"role": "user", "content": "你的任务是总结下面的对话内容:\n{}.请按照以下的格式总结上面的对话内容：\n"
                                                    "【用户和贾维斯正在做的事情】：\n"
                                                    "【其他内容】：".format(history)}
                    ],
                )
                message = response.choices[0].message
                _new_messages.append(ChatItem.new("user", message.content))
            self._messages = _new_messages

    def load_recent(self):
        return self._messages

    def clear_recent(self):
        self._messages = []
