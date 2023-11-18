import logging
import os
import threading
import time

import pygame
from openai import OpenAI

from config import system_config
from modules.mouth.mouth_interface import AbstractMouth


class OpenAIMouth(AbstractMouth):
    def __init__(self):
        self._logger = None
        self._client = None
        self._to_speak_list = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._client = OpenAI(api_key=system_config.OPENAI_MOUTH_API_KEY, base_url=system_config.OPENAI_MOUTH_API_BASE)

        # 初始化pygame，用于播放mp3文件
        pygame.mixer.init()
        # 设置音量 范围为0.0到1.0
        pygame.mixer.music.set_volume(system_config.BAIDU_MOUTH_VOICE_VOLUME)
        # 异步播放的语音等待队列
        self._to_speak_list = []

        threading.Thread(target=self.async_speak).start()

    def speak(self, content: str, finish_callback: callable):
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
        try:
            audio_file_path = os.path.join(system_config.TEMP_DIR_PATH, "audio.mp3")
            response = self._client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=content
            )
            response.stream_to_file(audio_file_path)

            # 加载音频文件
            pygame.mixer.music.load(audio_file_path)
            # 开始播放
            pygame.mixer.music.play()
            # 检查播放结束
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            # 这里需要另起线程执行callback逻辑，如果在本线程执行的话，callback函数中可能会有阻塞式wait_speak_finish的调用，这样就死锁了。
            threading.Thread(target=finish_callback).start()
        except Exception as e:
            self._logger.error("speak sentence failed, skip it, exception: {}".format(e))
