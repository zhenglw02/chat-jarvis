from modules.ear.ear_interface import AbstractEar
from config import const
from config.system_config import AI_NAME, PER_REQUEST_THRESHOLD_IN_SECOND

import websocket
import pyaudio

import threading
import time
import uuid
import json

CHUNK = 1024  # 每个缓冲区的帧数
FORMAT = pyaudio.paInt16  # 采样位数
CHANNELS = 1  # 单声道
RATE = 16000  # 采样频率


class BaiduEar(AbstractEar):
    def __init__(self):
        self._logger = None
        self._callback = None
        self._ws = None

        # 最近一次听到内容的时间，借此计算有多长时间没听到声音了，判断是不是用户说完了，在等待回答
        self._last_message_time = time.time()
        # 记录最近一次听到的完整内容
        self._last_sentence = ""
        # 上一次处理结束后，是否听到了新的内容，该标签和_last_message_time配合，以确定用户是否叫了AI，并在等待AI回答。
        self._have_new_voice = False
        # 休眠开关，当打开时，只有听到了AI自己的名字时才会响应，关闭时则处于持续对话过程中，不需要唤醒次即可与AI进行持续对话。
        self._sleep = True
        # 暂停开关，当其他组件在处理请求时，应打开暂停开关，暂停听力，否则可能会听到自己说的话，导致死循环
        self._pause = False

    def init(self, logger):
        self._logger = logger

    def start(self, callback):
        self._callback = callback

        self.check_finish_sentence()

        def run(*args):
            uri = const.URI + "?sn=" + str(uuid.uuid1())
            ws_app = websocket.WebSocketApp(uri,
                                            on_open=self.on_open,  # 连接建立后的回调
                                            on_message=self.on_message,  # 接收消息的回调
                                            on_error=self.on_error,  # 库遇见错误的回调
                                            on_close=self.on_close)  # 关闭后的回调
            self._ws = ws_app
            ws_app.run_forever()

        threading.Thread(target=run).start()

    def stop(self):
        self.send_finish(self._ws)

    def pause(self):
        self._logger.info("ear pause")
        self._pause = True

    def go_on(self):
        self._logger.info("ear go on")
        self._pause = False

    def sleep(self):
        self._logger.info("ear sleep")
        self._sleep = True

    def on_open(self, ws):
        """
        连接后发送数据帧
        :param  websocket.WebSocket ws:
        :return:
        """

        def run(*args):
            """
            发送数据帧
            :param args:
            :return:
            """
            self.send_start_params(ws)
            self.keep_listen(ws)
            self._logger.debug("thread terminating")

        threading.Thread(target=run).start()

    def on_message(self, ws, message):
        """
        接收服务端返回的消息
        :param ws:
        :param message: json格式，自行解析
        :return:
        """
        self._logger.debug("ear get response: " + message)
        m = json.loads(message)
        if m["type"] == "MID_TEXT" or m["type"] == "FIN_TEXT":
            self._last_message_time = time.time()
            self._last_sentence = m["result"]
            self._logger.debug("have_new_voice to true")
            self._have_new_voice = True

    def send_start_params(self, ws):
        """
        开始参数帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "START",
            "data": {
                "appid": const.APP_ID,  # 网页上的appid
                "appkey": const.API_KEY,  # 网页上的appid对应的appkey
                "dev_pid": const.DEV_PID,  # 识别模型
                "cuid": "yourself_defined_user_id",  # 随便填不影响使用。机器的mac或者其它唯一id，百度计算UV用。
                "sample": 16000,  # 固定参数
                "format": "pcm"  # 固定参数
            }
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        self._logger.debug("send START frame with params:" + body)

    def keep_listen(self, ws):
        p = pyaudio.PyAudio()  # 实例化对象
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)  # 打开流，传入响应参数

        while True:
            try:
                if not self._pause:
                    data = stream.read(2560)
                    ws.send(data, websocket.ABNF.OPCODE_BINARY)
                else:
                    time.sleep(0.2)
                    # 长时间不向服务端发请求，服务端会报错，因此暂停时定时发送一段空内容
                    ws.send(None, websocket.ABNF.OPCODE_BINARY)
            except Exception as e:
                self._logger.error(f"baidu_ear try listen and send data failed, exception: {e}")

    def send_finish(self, ws):
        """
        发送结束帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "FINISH"
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        self._logger.debug("send FINISH frame")

    def send_cancel(self, ws):
        """
        发送取消帧
        :param websocket.WebSocket ws:
        :return:
        """
        req = {
            "type": "CANCEL"
        }
        body = json.dumps(req)
        ws.send(body, websocket.ABNF.OPCODE_TEXT)
        self._logger.debug("send Cancel frame")

    def on_error(self, ws, error):
        """
        库的报错，比如连接超时
        :param ws:
        :param error: json格式，自行解析
        :return:
        """
        self._logger.error("ear get error: " + str(error))

    def on_close(self, a, b, c):
        """
        Websocket关闭
        :return:
        """
        self._logger.info("ws close ...")

    def check_finish_sentence(self):

        def run(*args):
            while True:
                duration = time.time() - self._last_message_time
                if duration > PER_REQUEST_THRESHOLD_IN_SECOND and self._have_new_voice:
                    if AI_NAME in self._last_sentence or not self._sleep:
                        self._logger.debug("have_new_voice to false, sleep to false")
                        self._have_new_voice = False
                        self._sleep = False

                        self._callback(self._last_sentence)
                time.sleep(0.1)

        threading.Thread(target=run).start()
