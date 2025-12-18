# Repository Guidelines

## 项目结构与模块划分
仓库入口 `main.py` 启动语音助手，运行参数位于 `config/system_config.py`。`modules/` 中按功能拆分耳朵、嘴巴、大脑、记忆等组件；`jarvis/jarvis.py` 负责调度；插件集中在 `plugin/`；项目运行过程中需持久化的数据放在 `system_data/`，如长期记忆等；运行产生的录音及缓存位于 `temp/`（可在配置中调整路径）。
- `modules/brain`: 大脑组件，本质是一个llm封装层，核心方法：handle_request，负责处理请求
- `modules/ear`: 耳朵组件，本质是语音转文字组件，需支持流式语音转文字，并自行决定用户语音何时结束
- `modules/mouth`: 嘴巴组件，本质是文字转语音组件，核心方法：speak，负责异步说出传入的文字
- `modules/memory`: 短期记忆组件，核心方法：load_data、save_data
- `modules/dashboard`: 仪表盘组件，核心方法：update_status、get_status
- `modules/long_memory`: 长期记忆组件，核心方法：save、search

## 构建、测试与开发命令
- `python3 -m venv .venv && source .venv/bin/activate`：创建并启用虚拟环境。
- `pip install -r requirements.txt`：安装 Python 依赖，macOS 需先用 Homebrew 安装 SDL/PortAudio，Linux 参照 README 安装 pyaudio 等包。
- `python3 main.py`：加载配置后启动 Jarvis，建议保留一个日志终端窗口便于定位异常。
若目录 `temp/` 不存在，请先 `mkdir -p temp`，并在 `config/system_config.py` 中填充百度与 OpenAI 凭证。

## 代码风格与命名规范
遵循 PEP 8，使用四个空格缩进、snake_case 函数与模块名、PascalCase 类名。插件文件保持 `xx_plugin.py` 模式并暴露清晰的入口函数；新增依赖需更新 `requirements.txt`。提交前可运行 `python -m black <file>` 统一格式，并为关键协程或 IO 函数补充 docstring。

## 测试指引
当前自动化覆盖有限，新增逻辑请用 `pytest` 编写模块级用例，在未来的 `tests/` 目录镜像真实结构（例：`tests/test_mouth.py`）。Mock OpenAI 与百度客户端，重点验证 Prompt 组装、异常恢复与消息流控制。合并前至少完成一次 `python3 main.py` 冒烟测试，确认耳朵、dashboard、嘴巴三段循环能顺利执行。

## 提交与 PR 指南
Git 历史偏好简短祈使句（如“增加openai版嘴巴”），提交主题控制在 72 字符内并说明涉及模块。PR 需写明问题背景、主要改动、手动测试证据（日志片段或截图）以及关联 issue/插件；若新增配置项，请同步说明如何在 `config/system_config.py` 设置密钥或路径。

## 安全与配置提示
凭证仅应保存在本地环境变量或未纳入版本控制的配置文件，勿提交 `temp/` 目录中的录音、日志或下载结果。插件若访问浏览器、文件系统或外部 API，需记录所需权限并对路径或 URL 做白名单校验，避免覆盖用户真实文件。
