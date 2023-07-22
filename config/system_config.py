# 角色名
AI_NAME = "贾维斯"

# 耳朵相关配置
# 聆听一段话时，等待多长时间没有声音则认为已说完，单位秒
PER_REQUEST_THRESHOLD_IN_SECOND = 1.0

# 嘴巴相关配置
# 音量大小，取值为0.0 ～ 1.0
VOICE_VOLUME = 0.5
# 说话语速，取值为0 ～ 9
SPEAK_SPEED = 5
# 发音人选择：度小美=0(默认)，度小宇=1，，度逍遥（基础）=3，度丫丫=4
SPEAK_PER = 3

# 大脑相关配置
# 使用的openai模型
OPENAI_MODEL = "gpt-3.5-turbo-0613"
OPENAI_API_KEY = "sk-xxx"
SYSTEM_PROMPT = f"你是一个人工智能管家，你的名字是{AI_NAME}。你本质上是我编写的一个程序，但你在和我交流时表现为一个专业的管家。\n" \
                f"你有耳朵，可以听到我说的话；你有嘴巴，可以说话；你有一个交互板，可以通过交互板获取我手动输入的文字；\n" \
                f"你有很多额外能力可以通过函数调用的方式使用，你应该注重函数的使用。\n" \
                f"你在和我交流时，应该表现的像是个人类，你是一个沉稳、体贴、有幽默感的人，你会照顾我的情绪，理解我话语里的情感，并基于我的情感与我对话。\n" \
                f"你不应该一直问我有什么需要帮助的，而应该主动发起话题。"


# 记忆相关配置
# 最多保存多长的记忆
MEMORY_MAX_LENGTH = 10
# 流式获取大脑返回的语音内容时，等待获取到多长的内容时开始说话。
START_SPEAK_CONTENT_LENGTH = 20

# 写代码插件相关配置
GENERATE_CODE_OPENAI_API_KEY = "sk-xxx"
# 写代码调用的模型和大脑使用的模型区分开，可以避免openai接口的限流
GENERATE_CODE_OPENAI_MODEL = "gpt-3.5-turbo"

# 提取摘要插件相关配置
SUMMARY_FILE_OPENAI_API_KEY = "sk-xxx"
SUMMARY_FILE_OPENAI_MODEL = "gpt-3.5-turbo-16k"
