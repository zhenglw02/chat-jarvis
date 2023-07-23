import logging
import time
import os
import threading

from aip import AipSpeech
import pygame

from modules.mouth.mouth_interface import AbstractMouth
from config import const
from config import system_config


class BaiduMouth(AbstractMouth):
    def __init__(self):
        self._logger = None
        self._client = None
        self._to_speak_list = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._client = AipSpeech(const.APP_ID_STR, const.API_KEY, const.SECRET_KEY)
        # 初始化pygame，用于播放mp3文件
        pygame.mixer.init()
        # 设置音量 范围为0.0到1.0
        pygame.mixer.music.set_volume(system_config.VOICE_VOLUME)
        # 异步播放的语音等待队列
        self._to_speak_list = []

        threading.Thread(target=self.async_speak).start()

    def speak(self, content: str, finish_callback):
        self._to_speak_list.append({'content': content, "finish_callback": finish_callback})

    def shutup(self):
        self._to_speak_list = []
        pygame.mixer.music.stop()
        pygame.mixer.music.rewind()

    def wait_speak_finish(self):
        while True:
            if len(self._to_speak_list) > 0:
                time.sleep(0.1)
            else:
                return

    def async_speak(self):
        while True:
            if len(self._to_speak_list) > 0:
                to_speak = self._to_speak_list[0]
                self.speak_one(to_speak.get('content'), to_speak.get('finish_callback'))
                try:
                    # 有可能用户点击了shutup，直接清空了队列，这里要兼容这种情况
                    self._to_speak_list.remove(to_speak)
                except Exception as e:
                    pass
            else:
                time.sleep(0.05)

    def speak_one(self, content: str, finish_callback):
        result = self._client.synthesis(content, 'zh', 1, {
            'vol': 5,
            'spd': system_config.SPEAK_SPEED,
            'per': system_config.SPEAK_PER,
        })

        # 识别正确返回语音二进制 错误则返回dict
        if not isinstance(result, dict):
            with open(os.path.join(const.TEMP_DIR_PATH, "audio.mp3"), 'wb') as f:
                f.write(result)
            # 加载音频文件
            pygame.mixer.music.load("./temp/audio.mp3")
            # 开始播放
            pygame.mixer.music.play()
            # 检查播放结束
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            # 这里需要另起线程执行callback逻辑，如果在本线程执行的话，callback函数中可能会有阻塞式wait_speak_finish的调用，这样就死锁了。
            threading.Thread(target=finish_callback).start()
        else:
            self._logger.error("tts failed: {}".format(result))
