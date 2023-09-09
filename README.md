# chat-jarvis

一个人工智能管家的开发框架。它定义了一个AI管家应具备的各种组件及组件之间的交互关系，如用于聆听用户语音的耳朵、用于思考的大脑，用于发出声音的嘴巴，用于以及通过手动输入与用户交互的交互板等。此外，它还定义了一套插件框架，用于为AI管家提供各种扩展功能。通过chat-jarvis，你不再需要坐在电脑前打字才能与ChatGPT等大语言模型对话，你可以用语音直接与它对话，甚至可以一边跑步一边让ChatGPT打开你家的空调。

chat-jarvis默认实现了一套组件：以百度智能云的实时语音识别服务为耳朵，以百度智能云的短文本在线合成服务为嘴巴，以OpenAI的接口为大脑。只要有百度智能云和OpenAI的账号，应该可以（借助新账号的免费羊毛）轻松运行chat-jarvis。如果不想使用默认的实现，你需要自行开发组件的实现类，或等待chat-jarvis支持更多组件的实现。

chat-jarvis默认集成了一些实验性质的插件，包括获取当前时间、生成代码、提取摘要、下载网页、管理日程等，需要注意的是，这些插件大多没有经过严格测试，性能并不稳定，使用起来需谨慎。你也可以按照插件的定义，自行开发更多插件，让你的贾维斯更为强大。

严格来说，chat-jarvis还只是一个小玩具，起因是当我用到ChatGPT时，我认为给它接上语音输入和输出，让它直接支持语音交流，在生活场景会更有用（工作场景下还是文字输入输出更有用），所以在业余时间做了些尝试。从目前的效果看，这个形式还是有很大的想象空间的，随着LLM的性能提升，以及更多插件的接入，我相信chat-jarvis会越来越强大。想拥有自己的贾维斯管家的同学，欢迎下载chat-jarvis，并定制属于自己的贾维斯，如果你愿意把你自己的贾维斯插件提交到本代码库中，让更多同学受益，我也是非常欢迎的。

# 安装运行

## 前置依赖

chat-jarvis默认使用百度智能云的语音相关服务和OpenAI的api作为贾维斯的组件实现，因此你需要：

- 拥有百度智能云账号
- 拥有OpenAI的账号
- 本地可以访问OpenAI的API接口

百度智能云的实时语音识别服务注册：https://ai.baidu.com/tech/speech/realtime_asr ，你需要注册一个账号并创建应用，然后领取免费资源：包括语音识别和语音合成部分。个人账号可以领取短文本在线合成服务5万次调用，以及实时语音识别服务10小时调用。

OpenAI的账号申请和API访问需要你自行准备（懂的都懂）。

## 运行配置

1. 克隆本代码库
2. 创建python venv并启动

```
cd chat-jarvis
python3 -m venv ./venv
source ./venv/bin/activate
```

3. 安装系统依赖，由于使用到了录音、展示窗口等功能，需要安装相关组件

```
# linux系统
sudo apt-get install -y python3-pyaudio python3-tk portaudio19-dev alsa-utils
# mac系统
brew install portaudio
```



3. 安装python依赖

```
pip3 install -r requirements.txt
```

4. 编辑服务参数

```
vi ./config/system_config.py

# 必须修改以下配置：
# 百度应用ID
BAIDU_EAR_APP_ID = 0
# 百度鉴权信息
BAIDU_EAR_API_KEY = "xxx"
BAIDU_EAR_SECRET_KEY = "xxx"
# 嘴巴相关配置
BAIDU_MOUTH_APP_ID = "0"
# 百度鉴权信息
BAIDU_MOUTH_API_KEY = "xxx"
BAIDU_MOUTH_SECRET_KEY = "xxx"
# 大脑使用的OpenAI key
BRAIN_OPENAI_API_KEY = "sk-xxx"
# 写代码插件相关配置
GENERATE_CODE_OPENAI_API_KEY = "sk-xxx"
# 提取摘要插件相关配置
SUMMARY_FILE_OPENAI_API_KEY = "sk-xxx"

# 其他参数可根据需要修改
```

5. 创建临时目录，临时目录用于存放贾维斯运行过程中产生的文件

```
# 默认临时目录为./temp，可以在./config/system_config.py中修改
mkdir ./temp
```

6. 运行main.py文件

```
python3 ./main.py
```

等贾维斯说完开场白，弹出交互窗口时，启动就已完成，可以进行对话了。

# TODOs

- 完善异常处理和失败自动恢复。目前有些逻辑没做异常处理，一旦因网络等原因失败就会导致贾维斯整体无响应，需要做一下异常处理和自动恢复。比如耳朵监听出异常的时候。
- 增加持久记忆能力。身为管家，贾维斯应该记住我的名字、性别、住址、爱好等个人特点，并在所有对话中都要考虑这些内容，而不是单轮对话中我告诉了他他才知道。
- 增加网络搜索插件。这是个很有用，也很复杂的插件，要做到能用很简单，要做到好用很难。
- 增加执行命令或python代码的插件。让贾维斯能够直接操纵我的电脑是个很危险也很刺激的事情，这需要他有更高的智慧，我前期做过一些测试，gpt-3.5大多数时候不能直接生成我想要的命令或代码，可能需要更好的大脑模型才能支持这个插件。
- 更多组件的实现类。现在贾维斯的耳朵和嘴巴依赖百度的服务，大脑依赖OpenAI的服务，后续可以考虑适配其他厂商的服务，或者用一些开源的模型。
- 已有插件的优化。这是个长期的事情，每个插件都需要做充分的测试和调优。