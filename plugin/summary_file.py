import logging
import os
import openai

from config import system_config, const

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis

openai.api_key = system_config.SUMMARY_FILE_OPENAI_API_KEY


class GenerateCodePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "summary_file"

    def get_chinese_name(self):
        return "提取摘要"

    def get_description(self):
        return "提取摘要接口，当你需要提取一个文件的摘要，或总结一个文件的主要内容时，你应该调用本接口，传入要总结的文件路径。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要总结的文件路径",
                }
            },
            "required": ["file_path"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        with open(os.path.join(const.TEMP_DIR_PATH, args.get("file_path")), "r") as f:
            content = f.read()
        response = openai.ChatCompletion.create(
            model=system_config.SUMMARY_FILE_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个资深的文字工作者."},
                {"role": "user", "content": "你的任务是总结下面的【输入内容】\n【输入内容】: {}".format(content)}
            ],
        )
        message = response.choices[0].message
        self._logger.debug("summary file result: \n{}\n".format(message.content))
        return PluginResult.new(
            result="文件内容总结如下：\n{}\n你应该优先考虑把上面的总结内容直接返回给我。".format(message.content),
            need_call_brain=True)
