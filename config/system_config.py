import logging

# 角色名
AI_NAME = "贾维斯"

# 临时文件保存地址
TEMP_DIR_PATH = "./temp"

# 系统配置
# 日志级别
LOG_LEVEL = logging.DEBUG

# 耳朵相关配置
# 百度应用ID
BAIDU_EAR_APP_ID = 36167526
# 百度语音识别地址，可以改为wss://
BAIDU_EAR_ASR_URI = "ws://vop.baidu.com/realtime_asr"
# 百度语言识别模型，可以修改为其它语言模型测试，如远场普通话19362
BAIDU_EAR_DEV_PID = 15372
# 百度鉴权信息
BAIDU_EAR_API_KEY = "vI2sOGUTNgphAvXACopM1i9a"
BAIDU_EAR_SECRET_KEY = "8CFuL8vGtmIPuHziij50LSenf9ALBxqX"
# 聆听一段话时，等待多长时间没有声音则认为已说完，单位秒
BAIDU_EAR_PER_REQUEST_THRESHOLD_IN_SECOND = 1.0

# 嘴巴相关配置
BAIDU_MOUTH_APP_ID = "36167526"
# 百度鉴权信息
BAIDU_MOUTH_API_KEY = "vI2sOGUTNgphAvXACopM1i9a"
BAIDU_MOUTH_SECRET_KEY = "8CFuL8vGtmIPuHziij50LSenf9ALBxqX"
# 音量大小，取值为0.0 ～ 1.0
BAIDU_MOUTH_VOICE_VOLUME = 0.5
# 说话语速，取值为0 ～ 9
BAIDU_MOUTH_SPEAK_SPEED = 5
# 发音人选择：度小美=0(默认)，度小宇=1，，度逍遥（基础）=3，度丫丫=4
BAIDU_MOUTH_SPEAK_PER = 3

# 大脑相关配置
# 使用的openai模型
BRAIN_OPENAI_MODEL = "gpt-3.5-turbo"
BRAIN_OPENAI_API_KEY = "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"
BRAIN_OPENAI_SYSTEM_PROMPT = f"你是一个人工智能管家，你的名字是{AI_NAME}。你本质上是我编写的一个程序，但你在和我交流时表现为一个专业的管家。\n" \
                f"你有耳朵，可以听到我说的话；你有嘴巴，可以说话；你有一个交互板，可以通过交互板获取我手动输入的文字；\n" \
                f"你有很多额外能力可以通过函数调用的方式使用，你应该注重函数的使用。\n" \
                f"你在和我交流时，应该表现的像是个人类，注意不要让我觉得你是一个AI。\n" \
                f"你是一个沉稳、体贴、有幽默感的人，你会照顾我的情绪，理解我话语里的情感，并基于我的情感与我对话。\n" \
                f"你不应该一直问我有什么需要帮助的，而应该主动发起话题。"
# 流式获取大脑返回的语音内容时，等待获取到多长的内容时开始说话。
START_SPEAK_CONTENT_LENGTH = 20

# 记忆相关配置
# 最多保存多长的记忆
MEMORY_MAX_LENGTH = 10

# 写代码插件相关配置
GENERATE_CODE_OPENAI_API_KEY = "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"
GENERATE_CODE_OPENAI_MODEL = "gpt-3.5-turbo-0613"

# 提取摘要插件相关配置
SUMMARY_FILE_OPENAI_API_KEY = "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"
SUMMARY_FILE_OPENAI_MODEL = "gpt-3.5-turbo-16k"
