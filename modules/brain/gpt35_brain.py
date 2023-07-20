import logging
import openai
from config.system_config import AI_NAME, OPENAI_MODEL, OPENAI_API_KEY, START_SPEAK_CONTENT_LENGTH
from modules.brain.brain_interface import AbstractBrain
from modules.memory.memory_interface import AbstractMemory
from openai.error import RateLimitError
from modules.brain.brain_interface import ChatItem
from modules.brain.util import is_break_char

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
        self._memory.save(ChatItem.new("system", system_prompt))

    def handle_request(self, chat_item: ChatItem, result_callback):
        self._memory.save(chat_item)
        chat_items = self._memory.load_recent()
        messages = []
        for item in chat_items:
            messages.append(chat_item_to_message(item))
        self._logger.debug("chat with messages: {}".format(messages))
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=messages,
                functions=self._functions,
                stream=True,
            )
            is_function_call = False
            collected_messages = []
            total_content = ""
            temp_content = ""
            for chunk in response:
                chunk_message = chunk['choices'][0]['delta']  # extract the message
                collected_messages.append(chunk_message)  # save the message
                if len(collected_messages) == 1 and 'function_call' in chunk_message:
                    is_function_call = True

                if not is_function_call and 'content' in chunk_message:
                    total_content += chunk_message['content']
                    temp_content += chunk_message['content']
                    if is_break_char(chunk_message['content']) and len(temp_content) >= START_SPEAK_CONTENT_LENGTH:
                        result_callback(ChatItem.new("assistant", temp_content), False)
                        temp_content = ""

            total_chat_item = merge_collected_messages(collected_messages, is_function_call)
            self._memory.save(total_chat_item)
            if is_function_call:
                result_callback(total_chat_item, True)
            else:  # 即使temp_content为空也要回调，告诉外界已经说完
                result_callback(ChatItem.new("assistant", temp_content), True)
        except RateLimitError as e:
            fake_rate_limit_message = ChatItem.new("assistant", "我的大脑被限流了，请等待一分钟再和我说话")
            result_callback(fake_rate_limit_message, True)


def chat_item_to_message(chat_item: ChatItem):
    message = {
        "role": chat_item.role,
        "content": chat_item.content,
    }
    if chat_item.name is not None:
        message["name"] = chat_item.name
    if chat_item.function_call is not None:
        message["function_call"] = chat_item.function_call
    return message


def merge_collected_messages(collected_messages, is_function_call) -> ChatItem:
    total_chat_item = ChatItem.new("assistant", "")
    if is_function_call:
        total_chat_item.content = None
        total_chat_item.function_call = {
            "name": collected_messages[0]["function_call"]["name"],
            "arguments": "",
        }

    # 最后一个是空的
    for m in collected_messages[:len(collected_messages) - 1]:
        if is_function_call:
            total_chat_item.function_call["arguments"] += m["function_call"]["arguments"]
        else:
            total_chat_item.content += m["content"]

    return total_chat_item
