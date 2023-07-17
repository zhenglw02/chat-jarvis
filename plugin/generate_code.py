import logging
import openai
from config import system_config

from plugin.plugin_interface import AbstractPlugin, PluginResult

openai.api_key = system_config.GENERATE_CODE_OPENAI_API_KEY


class GenerateCodePlugin(AbstractPlugin):
    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "generate_code"

    def get_chinese_name(self):
        return "生成代码"

    def get_description(self):
        return "生成代码接口，当你需要生成代码时你应该调用本接口，而不应该自己直接生成代码。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "生成代码的要求",
                }
            },
            "required": ["request"],
        }

    def run(self, args: dict) -> PluginResult:
        response = openai.ChatCompletion.create(
            model=system_config.GENERATE_CODE_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个代码生成器。你的任务是根据要求生成符合要求的代码。"},
                {"role": "user", "content": args.get("request")}
            ],
        )
        message = response.choices[0].message
        self._logger.debug("code gen result: \n{}\n".format(message.content))
        return PluginResult.new(result=message.content, need_call_brain=True)
