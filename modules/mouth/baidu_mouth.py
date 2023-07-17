import logging
import time

from aip import AipSpeech
import pygame

from modules.mouth.mouth_interface import AbstractMouth
from config.const import APP_ID_STR, API_KEY, SECRET_KEY
from config import system_config


class BaiduMouth(AbstractMouth):
    def __init__(self):
        self._logger = None
        self._client = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._client = AipSpeech(APP_ID_STR, API_KEY, SECRET_KEY)
        # 初始化pygame，用于播放mp3文件
        pygame.mixer.init()
        # 设置音量 范围为0.0到1.0
        pygame.mixer.music.set_volume(system_config.VOICE_VOLUME)

    def speak(self, content: str, finish_callback):
        result = self._client.synthesis(content, 'zh', 1, {
            'vol': 5,
            'spd': system_config.SPEAK_SPEED,
            'per': system_config.SPEAK_PER,
        })

        # 识别正确返回语音二进制 错误则返回dict
        if not isinstance(result, dict):
            with open('./temp/audio.mp3', 'wb') as f:
                f.write(result)
            # 加载音频文件
            pygame.mixer.music.load("./temp/audio.mp3")
            # 开始播放
            pygame.mixer.music.play()
            # 检查播放结束
            # todo: 支持指定是否阻塞等待
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            finish_callback()
        else:
            self._logger.error("tts failed: {}".format(result))
