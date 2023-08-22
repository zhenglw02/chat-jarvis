import logging
import requests

from plugin.plugin_interface import AbstractPlugin, PluginResult
from config import system_config
from jarvis.jarvis import Jarvis


class GoogleSearchPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return system_config.GOOGLE_SEARCH_ENABLE and \
            system_config.GOOGLE_SEARCH_CX != "" and system_config.GOOGLE_SEARCH_API_KEY != ""

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "google_search"

    def get_chinese_name(self):
        return "搜索谷歌"

    def get_description(self):
        return "搜索谷歌接口。本接口接收一个搜索关键词，然后调用谷歌API进行搜索。" \
               "当你对于用户输入的内容感到不理解，或认为需要更多信息才能够回答用户的问题时，你应该调用本接口。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要搜索的query",
                }
            },
            "required": ["query"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": system_config.GOOGLE_SEARCH_API_KEY,
            "cx": system_config.GOOGLE_SEARCH_CX,
            "q": args.get('query'),
            "start": 0,
            "num": 5,
        }
        response = requests.get(base_url, params=params)
        data = response.json()
        result = "以下是从谷歌中搜索到的网页及其摘要：\n"
        for item in data.get('items'):
            result += "【网页标题】：{}\n".format(item.get('title'))
            result += "【摘要】：{}\n".format(item.get('snippet'))
            result += "【网页链接】：{}\n\n".format(item.get('link'))

        result += "如果上述网页的摘要已经足够让你回答用户的问题或者继续与用户对话，那么你可以直接与用户继续对话。\n" \
                  "如果上述网页的摘要没有足够的信息，那么你应该按照用户的需要，选择其中一至二个与用户问题最相关且最专业的网页，使用【下载网页内容】接口获取这些网页的详细内容，再根据网页的详细内容与用户继续对话。"
        return PluginResult.new(result=result, need_call_brain=True)
