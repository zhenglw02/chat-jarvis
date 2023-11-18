import logging
import threading
import time

import cv2
from aip import AipBodyAnalysis
from aip import AipImageClassify

from config import system_config
from modules.eye.eye_interface import AbstractEye


class BaiduEye(AbstractEye):

    def __init__(self):
        self._logger = None
        self._cap = None
        self._enabled = None
        self._stopping = None
        self._snapshot = None

    def init(self, logger: logging.Logger):
        self._logger = logger
        self._cap = cv2.VideoCapture(0)  # 0 表示默认摄像头，如果有多个摄像头，可以尝试使用1、2、3等
        self._enabled = False
        threading.Thread(target=self._open_camera).start()

    def open(self):
        if not self._cap:
            self._cap = cv2.VideoCapture(0)  # 0 表示默认摄像头，如果有多个摄像头，可以尝试使用1、2、3等
        self._enabled = True
        self._stopping = False

    def close(self):
        self._enabled = False
        self._stopping = True

    def enabled(self):
        return self._enabled

    def parse_snapshot(self):
        if not self._enabled:
            return None

        msg = _gesture(self._snapshot)
        # 物体检测得到的信息不够精确，效果不好，暂时不加
        # msg += _object_detect(self._snapshot)
        msg += _body_attr(self._snapshot)
        return msg

    def _open_camera(self):

        while True:
            if self._enabled:
                # 读取一帧
                ret, frame = self._cap.read()

                # 在窗口中显示帧
                cv2.imshow("jarvis's eye", frame)

                # 检测按键，如果按下Esc键，退出循环
                # 必须有这段逻辑，否则摄像头功能不正常
                if cv2.waitKey(1) == 27:  # 27是Esc键的ASCII码
                    break

                # 将帧编码为JPEG格式
                _, jpeg_encoded = cv2.imencode('.jpg', frame)

                # 将JPEG编码后的数据转换为字节流
                jpeg_bytes = jpeg_encoded.tobytes()
                self._snapshot = jpeg_bytes
            elif self._stopping:
                # 释放摄像头资源
                self._cap.release()
                self._cap = None
                self._stopping = False
            else:
                time.sleep(1)


# 手势识别
def _gesture(snapshot):
    APP_ID = system_config.BAIDU_EYE_BODY_ATTR_APP_ID
    API_KEY = system_config.BAIDU_EYE_BODY_ATTR_API_KEY
    SECRET_KEY = system_config.BAIDU_EYE_BODY_ATTR_SECRET_KEY

    client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
    result = client.gesture(snapshot)
    if result is None or result == {}:
        return ""
    results = result['result']
    if len(results) == 0:
        return ""

    infos = []
    for r in results:
        classname = _gesture_class_map(r['classname'])
        probability = r['probability']
        if classname != "":
            infos.append(f"内容：{classname}，概率：{probability}\n")

    if len(infos) == 0:
        return ""

    return_msg = "以下是你看到的关于用户手势的信息：\n"
    for info in infos:
        return_msg += info
    return return_msg


def _gesture_class_map(classname):
    class_map = {
        "One": "数字1",
        "Five": "数字5",
        "Fist": "握起拳头",
        "OK": "好的",
        "Prayer": "双手合十，可能是祈祷",
        "Congratulation": "作揖，表示礼貌",
        "Honour": "作别，表示告别",
        "Heart_single": "单手比心",
        "Thumb_up": "点赞，表示赞赏",
        "Thumb_down": "嘲讽的手势",
        "ILY": "rock或说唱的手势",
        "Palm_up": "掌心向上",
        "Heart_1": "双手比心",
        "Heart_2": "双手比心",
        "Heart_3": "双手比心",
        "two": "数字2",
        "three": "数字3",
        "four": "数字4",
        "six": "数字6",
        "seven": "数字7",
        "eight": "数字8",
        "nine": "数字9",
        "Rock": "rock的手势",
        "Insult": "竖中指",
        "Face": "一张人脸"
    }
    if classname not in class_map:
        return ""
    else:
        return class_map[classname]


# 人体检测
def _body_attr(snapshot):
    APP_ID = system_config.BAIDU_EYE_BODY_ATTR_APP_ID
    API_KEY = system_config.BAIDU_EYE_BODY_ATTR_API_KEY
    SECRET_KEY = system_config.BAIDU_EYE_BODY_ATTR_SECRET_KEY

    client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
    result = client.bodyAttr(snapshot)
    if result is None or result == {}:
        return ""

    infos = []
    infos.append(f"图像中有{result['person_num']}个人。\n")
    if result['person_info'] is not None and len(result['person_info']) > 0:
        for i in result['person_info']:
            attrs = []
            for k, v in i['attributes'].items():
                if v['name'] != '不确定':
                    attrs.append(v['name'])
            attr = ",".join(attrs)
            infos.append(f"图像中的人物特征为：{attr}")

    if len(infos) == 0:
        return ""

    return_msg = "以下是你看到的关于图像中人物的信息：\n"
    for info in infos:
        return_msg += info
    return return_msg


# 通用物体检测 + 图像主体检测，效果不好
def _object_detect(snapshot):
    APP_ID = system_config.BAIDU_EYE_IMAGE_APP_ID
    API_KEY = system_config.BAIDU_EYE_IMAGE_API_KEY
    SECRET_KEY = system_config.BAIDU_EYE_IMAGE_SECRET_KEY

    client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
    scenes = ['advanced_general', 'multi_object_detect']
    """ 调用组合接口API 传入参数为图片, 数组"""
    response = client.combinationByImage(snapshot, scenes)
    if response is None or response == {}:
        return ""
    result = response['result']
    if result is None or result == {}:
        return ""

    infos = []
    advanced_general_result = result['advanced_general']
    if advanced_general_result is not None and advanced_general_result != {} and len(
            advanced_general_result['result']) > 0:
        items = []
        for r in advanced_general_result['result']:
            if r['score'] > 0.25:
                items.append(r['keyword'])
        infos.append(",".join(items) + "\n")

    object_detect_result = result['multi_object_detect']
    if object_detect_result is not None and object_detect_result != {} and len(object_detect_result['result']) > 0:
        items = []
        for r in object_detect_result['result']:
            if r['score'] > 0.25:
                items.append(r['name'])
        infos.append(",".join(items) + "\n")

    if len(infos) == 0:
        return ""

    return_msg = "以下是你看到的关于图像中主体的信息：\n"
    for info in infos:
        return_msg += info
    return return_msg


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format='[%(asctime)-15s] [%(funcName)s()][%(levelname)s] %(message)s')
    logger.setLevel(system_config.LOG_LEVEL)

    eye = BaiduEye()
    eye.init(logger)

    eye.open()
    print(eye.enabled())
    time.sleep(2)

    info = eye.parse_snapshot()
    print(info)

    eye.close()
    print(eye.enabled())

    eye.open()
    print(eye.enabled())

    eye.close()
