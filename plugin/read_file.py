import logging

from plugin.plugin_interface import AbstractPlugin, PluginResult
from jarvis.jarvis import Jarvis


class ReadFilePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "read_file"

    def get_chinese_name(self):
        return "读取文件"

    def get_description(self):
        return "读取文件内容接口，当你需要读取一个文件的内容时，你应该调用本接口，传入要读取的文件路径。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件路径，应该是绝对路径。",
                }
            },
            "required": ["file_path"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        file_path = args.get("file_path")
        with open(file_path, "r") as f:
            content = f.read()
        return PluginResult.new(result="文件内容如下：\n{}".format(content), need_call_brain=True)
