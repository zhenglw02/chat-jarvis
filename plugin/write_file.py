import logging
import os
import time

from config import system_config

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class WriteFilePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return False

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "write_file"

    def get_chinese_name(self):
        return "写入文件"

    def get_description(self):
        return "写入文件内容接口，当你需要向一个文件中写入内容时，你应该调用本接口，传入要写入的内容。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "要写入的内容",
                },
            },
            "required": ["file_path", "content"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        file_name = f"write_file-{str(int(time.time()))}.md"
        file_path = os.path.abspath(os.path.join(system_config.TEMP_DIR_PATH, file_name))
        with open(file_path, "w") as f:
            f.write(args.get("content"))
        return PluginResult.new(result="已将内容写入到文件【{}】中。".format(file_path), need_call_brain=True)
