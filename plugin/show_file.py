import logging
import subprocess
import platform
import os

from plugin.plugin_interface import AbstractPlugin, PluginResult
from config import const
from jarvis.jarvis import Jarvis


class ShowFilePlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "show_file"

    def get_chinese_name(self):
        return "展示文件"

    def get_description(self):
        return "展示文件内容给用户，当你需要把一个文件中的内容展示给我时，你应该调用本接口，传入文件的路径。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要展示的文件的路径",
                }
            },
            "required": ["file_path"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        try:
            file_path = os.path.join(const.TEMP_DIR_PATH, args.get('file_path'))
            # 获取当前操作系统
            current_os = platform.system()

            # 根据操作系统来选择相应的打开命令
            if current_os == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            elif current_os == 'Windows':  # Windows
                subprocess.run(['start', '', file_path], shell=True)
            elif current_os == 'Linux':  # Linux
                # 使用xdg-open打开Markdown文件
                # xdg-open会自动调用系统中与Markdown相关的默认应用程序
                subprocess.run(['xdg-open', file_path])
            else:
                self._logger.error(f"unknown platform system: {current_os}")
                jarvis.mouth.speak("未知的操作系统，无法展示文件。", lambda: {})
        except Exception as e:
            self._logger.error(f"execute open file command failed, exception: {e}")
            jarvis.mouth.speak("展示文件失败。", lambda: {})

        # 节约openai接口调用次数，展示出内容后就不调大脑了，返回调了也只会得到几句没意义的话
        return PluginResult.new(result="done", need_call_brain=False)
