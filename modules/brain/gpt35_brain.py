import logging
import openai
from config.system_config import AI_NAME, OPENAI_MODEL, OPENAI_API_KEY
from modules.brain.brain_interface import AbstractBrain
from modules.memory.memory_interface import AbstractMemory
from openai.error import RateLimitError

openai.api_key = OPENAI_API_KEY

system_prompt = "你是一个人工智能管家，你的名字是{}。".format(AI_NAME)


class GPT35Brain(AbstractBrain):
    def __init__(self):
        self._logger = None
        self._client = None

        self._functions = None
        self._memory = None

    def init(self, logger: logging.Logger, functions, memory: AbstractMemory):
        self._logger = logger
        self._functions = functions
        self._memory = memory
        self._memory.save({"role": "system", "content": system_prompt})

    def handle_request(self, message, message_callback):
        self._memory.save(message)
        messages = self._memory.load_recent()
        self._logger.debug("chat with messages: {}".format(messages))
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=messages,
                functions=self._functions,
            )
            message = response.choices[0].message
            self._logger.debug("chat response: %s", message)

            self._memory.save(message)
            message_callback(message)
        except RateLimitError as e:
            fake_rate_limit_message = {"role": "assistant", "content": "我的大脑被限流了，请等待一分钟再和我说话"}
            message_callback(fake_rate_limit_message)
