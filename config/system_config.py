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

# 记忆相关配置
# 最多保存多长的记忆
MEMORY_MAX_LENGTH = 10
# 流式获取大脑返回的语音内容时，等待获取到多长的内容时开始说话。
START_SPEAK_CONTENT_LENGTH = 20

# 写代码插件相关配置
GENERATE_CODE_OPENAI_API_KEY = "sk-xxx"
# 写代码调用的模型和大脑使用的模型区分开，可以避免openai接口的限流
GENERATE_CODE_OPENAI_MODEL = "gpt-3.5-turbo"
