import logging
import openai
import os
import time
from config import system_config

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis

openai.api_key = system_config.GENERATE_CODE_OPENAI_API_KEY


class GenerateCodePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

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

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        response = openai.ChatCompletion.create(
            model=system_config.GENERATE_CODE_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个代码生成器。你的任务是根据要求生成符合要求的代码。"},
                {"role": "user", "content": args.get("request")}
            ],
        )
        message = response.choices[0].message
        self._logger.debug("code gen result: \n{}\n".format(message.content))
        file_name = f"generate_code-{str(int(time.time()))}.md"
        with open(os.path.join(system_config.TEMP_DIR_PATH, file_name), "w") as f:
            f.write(message.content)
        return PluginResult.new(
            result=f"已经将代码生成到文件【{file_name}】中，你应该倾向于使用展示文件插件将代码文件展示给我，除非我明确要求使用其他方式将代码文件给我。",
            need_call_brain=True)
