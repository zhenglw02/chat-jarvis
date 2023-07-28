import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from plugin.plugin_interface import AbstractPlugin, PluginResult
from config import system_config
from jarvis.jarvis import Jarvis


class DownloadURLPlugin(AbstractPlugin):
    def valid(self) -> bool:
        return True

    def __init__(self):
        self._logger = None

    def init(self, logger: logging.Logger):
        self._logger = logger

    def get_name(self):
        return "download_url"

    def get_chinese_name(self):
        return "下载网页"

    def get_description(self):
        return "下载网页接口，当你需要下载某个url的内容时，你应该调用本接口。\n" \
               "当我的输入内容是一个网页url时，你应该优先考虑调用本接口下载网页内容，然后再对网页内容进行下一步的处理，以满足我的需求。"

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "要下载的网页url",
                }
            },
            "required": ["url"],
        }

    def run(self, jarvis: Jarvis, args: dict) -> PluginResult:
        # 设置ChromeOptions以启动headless浏览器
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        # 需要本地安装了chromeDriver
        driver = webdriver.Chrome(options=chrome_options)

        try:
            # 最长等待时间（秒），等待页面加载完成
            wait_time = 10
            driver.get(args['url'])

            # 使用WebDriverWait等待页面加载完成
            WebDriverWait(driver, wait_time).until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'body')))

            # 获取页面内容
            page_content = driver.page_source

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(page_content, 'html.parser')

            # 找到页面中的所有文本内容
            text_content = soup.get_text()
            file_name = "download_url-{}.txt".format(str(int(time.time())))
            with open(os.path.join(system_config.TEMP_DIR_PATH, file_name), "w") as f:
                f.write(text_content)

        finally:
            # 关闭浏览器
            driver.quit()

        return PluginResult.new(result=f"我以将该网页的内容下载到文件【{file_name}】中", need_call_brain=True)
