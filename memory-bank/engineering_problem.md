# 工程问题记录

## 记录范围

记录按 `memory-bank/plan.md` 推进时遇到的工程问题、底层原因和处理方式。不记录密钥、密码、完整服务 URI 或其他敏感值。

## 总览

| 步骤 | 当前状态 | 主要工程问题 | 当前处理 |
| --- | --- | --- | --- |
| 第 1 步 | 已通过 | `venv` 缺 `ensurepip`；`adb` 未检测到 | 改用 `virtualenv` 创建 `.venv`；`adb` 留到第 5 步 |
| 第 2 步 | 已通过 | 凭据文件不存在或字段为空 | 在仓库外创建 `credentials.env`，权限设为 `600` |
| 第 3 步 | 已通过 | 代理、Neo4j URI、Pinecone SDK 问题 | 忽略本地代理；使用安全 Neo4j scheme；补 Pinecone SDK |
| 第 4 步 | 已通过 | Docker 受容器权限限制；权重、依赖、OCR 和启动路径问题 | 使用本地非 Docker backend，并对 OmniParser 做兼容降级 |
| 第 5 步 | 已通过 | 初始无 ADB/设备；模拟器无 KVM；ADB 路径混用；截图路径不可写 | 安装 Android SDK 和 AVD；使用 SDK ADB；截图回退到 `/data/local/tmp` |
| 第 6 步 | 已通过 | backend 需重启；OpenAI/LangChain 依赖冲突；Gradio 回调 outputs 不匹配 | 重启本地 backend；调整依赖；修复 `demo.py` 回调返回值 |

## 第 1 步：环境准备

- 问题：`python3 -m venv .venv` 失败，提示 `ensurepip` 不可用。
- 原因：系统缺少 `python3-venv` 或 `ensurepip`。
- 处理：改用 `python3 -m virtualenv .venv` 创建仓库根目录虚拟环境。
- 结果：核心依赖、项目导入、Torch 与 CUDA 检查通过。
- 遗留：`adb` 未检测到，放到第 5 步设备连接阶段处理。

## 第 2 步：外部服务凭据

- 问题：`/home/tiger/.config/appagentx/credentials.env` 最初不存在或字段为空。
- 原因：凭据文件尚未创建，必要字段尚未填写。
- 处理：在仓库外创建凭据文件，补全 LLM、Neo4j、Pinecone 字段，权限设置为 `600`。
- 验证：新增 `scripts/verify-step2-credentials.sh` 检查字段、权限和仓库外位置。
- 结果：字段完整，权限正确，未把真实密钥写入仓库。

## 第 3 步：配置与外部连通性

- 问题：真实 API Key 不能写进 `AppAgentX/config.py`。
- 处理：`config.py` 改为从仓库外 `credentials.env` 加载配置。
- 问题：LLM 初次连接报 `Connection refused`。
- 原因：环境代理指向 `127.0.0.1:7890`，但本地代理服务不可用。
- 处理：验证脚本忽略环境代理。
- 问题：Neo4j 报 `Unable to retrieve routing information`。
- 原因：Aura 实例需要安全连接 scheme。
- 处理：将 URI 调整为安全 scheme，例如 `neo4j+s://...`。
- 问题：缺少 Pinecone SDK，报 `ModuleNotFoundError: No module named 'pinecone'`。
- 处理：在 `AppAgentX/requirements.txt` 补充 Pinecone 依赖。
- 结果：LLM、Neo4j、Pinecone 连通性验证通过。

## 第 4 步：Backend 服务

### Docker 路线失败

- 报错：`Cannot connect to the Docker daemon at unix:///var/run/docker.sock`。
- 原因：当前环境里 Docker daemon 未正常运行。
- 处理：尝试手动启动 `dockerd`。

- 报错：`failed to create NAT chain DOCKER`、`Permission denied`。
- 原因：当前容器环境没有足够的网络和 iptables 权限。
- 处理：尝试用 `--iptables=false --ip-masq=false --bridge=none` 绕过默认网络配置。

- 报错：BuildKit 构建时报 `failed to mount ... operation not permitted`。
- 报错：拉取镜像时报 `failed to register layer: unshare: operation not permitted`。
- 底层原因：当前会话仍在容器内，缺少 Docker 构建、镜像解包和 namespace 操作所需的宿主权限。
- 结论：在当前容器环境内，Docker Compose 启动 backend 不可用。需要宿主机 Docker、privileged 容器，或采用本地非 Docker 启动。

### 权重文件问题

- 报错：`missing_or_empty_file: .../weights/icon_detect_v1_5/best.pt`。
- 原因：OmniParser 权重下载不完整，且远端 `icon_detect_v1_5` 使用的是 `model_v1_5.pt`，不是 `model.safetensors`。
- 处理：下载 `icon_detect_v1_5/model_v1_5.pt`，复制为 `icon_detect_v1_5/best.pt`，满足现有代码路径。
- 结果：`best.pt` 存在且非空，约 `39M`；`icon_caption_florence` 目录存在。

### 本地非 Docker 替代方案
不用 Docker Compose。原因是当前环境里 Docker 构建和镜像解包会触发 mount/unshare operation not permitted，不是项目代码问题，而是容器权限问题。

替代方式是：在仓库根目录使用 .venv，直接用 uvicorn 启动两个 FastAPI 服务。

- 方案：直接用 `.venv` 启动两个 FastAPI 服务：ImageEmbedding 端口 `8001`，OmniParser 端口 `8000`。

- 报错：NumPy ABI 警告，提示 `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6`。
- 原因：`torch==2.2.0` 与已安装的 `numpy==2.2.6` 不兼容。
- 处理：固定 `numpy==1.26.4`。

- 报错：`transformers` 提示 PyTorch 版本不足，随后出现 `NameError: name 'nn' is not defined`。
- 原因：后端依赖未固定，安装了过新的 `transformers`，该版本要求 PyTorch >= 2.4。
- 处理：将 OmniParser 依赖固定为 `transformers==4.40.2`，与权重配置更匹配。

- 报错：`ModuleNotFoundError: No module named 'langchain_text_splitters'`。
- 原因：`paddleocr/paddlex` 的间接依赖未完整安装。
- 处理：补装 `langchain-text-splitters`。

- 报错：EasyOCR 启动时下载检测模型超时，`urllib.error.URLError: <urlopen error [Errno 110] Connection timed out>`。
- 原因：`utils.py` 在模块导入时立即执行 `easyocr.Reader(['en'])`，服务启动阶段就触发外网模型下载。
- 处理：将 EasyOCR 和 PaddleOCR 初始化改为 lazy 初始化，实际请求时再创建对象，避免服务启动被下载阻塞。

- 报错：`FileNotFoundError: weights/icon_detect_v1_5/best.pt`。
- 原因：`omni.py` 使用相对路径 `weights/...`。如果从仓库根目录用 `--app-dir` 启动，当前工作目录不在 `AppAgentX/backend/OmniParser`，相对路径会解析失败。
- 处理：启动 OmniParser 时必须先 `cd AppAgentX/backend/OmniParser`，再运行 `../../../.venv/bin/python -m uvicorn omni:app --host 0.0.0.0 --port 8000`。

- 报错：`Unknown argument: det_db_score_mode`。
- 原因：当前环境中的 PaddleOCR 3.x 不再接受旧版 PaddleOCR 初始化参数。
- 处理：改用 PaddleOCR 3.x 参数，并将 OCR 输出适配为 `rec_texts/rec_scores/rec_polys` 结构。

- 报错：`ConvertPirAttribute2RuntimeAttribute not support ...`。
- 原因：PaddleOCR/PaddlePaddle 3.x 在当前环境触发 PIR/oneDNN 执行路径异常。
- 处理：将 PaddleOCR 调用改为可降级；PaddleOCR 失败时跳过 OCR 文本框，继续用 YOLO + Florence 解析界面元素。

- 报错：`'NoneType' object is not iterable`、`list indices must be integers or slices, not str`。
- 原因：OCR 降级为空后，OmniParser 内部存在空 OCR 框和 bbox/dict 结构不一致问题。
- 处理：空 OCR 框统一为 `[]`，`remove_overlap_new()` 在无 OCR 分支也返回 dict 结构。

- 结果：ImageEmbedding 与 OmniParser 本地服务验证通过；`/process_image/` 可返回元素，最终输出 `step4_backend_services_ok`。

## 第 5 步：Android 设备连接

- 问题：初始运行第 5 步验证脚本输出 `adb_missing`。
- 原因：系统没有可用 ADB，或 ADB 不在 `PATH`。
- 处理：安装 Android SDK Platform Tools，并优先使用 `/home/tiger/android-sdk/platform-tools/adb`。

- 问题：安装 ADB 后输出 `adb_no_devices`，本地平板无法直接用于远程实验机。
- 原因：ADB 设备必须被运行实验的远程机器访问，本地未连接到远程机器的设备不会出现在远程 `adb devices`。
- 处理：改用 Android emulator 作为第 5 步目标设备。

- 问题：当前环境没有 `/dev/kvm`。
- 原因：远程容器或宿主环境未暴露 KVM 设备。
- 处理：创建 `appagentx_api36` AVD 后用 `-accel off` 无窗口模式启动；该模式较慢，但可完成 ADB 验证。

- 问题：直连 `adb shell wm size` 成功，但项目 `get_device_size` 初次失败。
- 原因：系统 `/usr/bin/adb` 与 Android SDK ADB 混用，项目内部 shell 命令解析到旧路径。
- 处理：`scripts/verify-step5-adb.py` 在运行前把 Android SDK `platform-tools` 放到 `PATH` 前面。

- 问题：`take_screenshot` 写入 `/sdcard/...` 失败，报 `Saving image failed`。
- 原因：当前 emulator 的 `/sdcard` 路径不可写或外部存储未按预期挂载。
- 处理：`AppAgentX/tool/screen_content.py` 的截图逻辑增加 `/data/local/tmp` 备用路径。

- 结果：`emulator-5554` 在线，屏幕尺寸 `1080x1920`，项目工具尺寸匹配，截图成功，输出 `step5_adb_device_ok`。

## 第 6 步：运行 Demo

- 问题：第 6 步前置验证中 `8001/available_models` 报 `Connection refused`。
- 原因：ImageEmbedding 服务进程已退出或端口残留状态不一致。
- 处理：重启 ImageEmbedding 和 OmniParser 两个本地 uvicorn 服务，再继续 Demo。

- 问题：启动 `demo.py` 报 `AttributeError: module 'openai' has no attribute 'DefaultHttpxClient'`。
- 原因：第 4 步安装 OmniParser 依赖时将 `openai` 降到 `1.3.5`，但当前 `langchain-openai` 需要新版 OpenAI SDK。
- 处理：升级 OpenAI SDK 到 `>=2.26,<3`。

- 问题：启动 `demo.py` 报 `ModuleNotFoundError: No module named 'langchain.prompts'`。
- 原因：当前 LangChain 1.x 已移除项目代码依赖的旧 import 路径。
- 处理：将 LangChain 相关包调整为 0.3 系列兼容组合。

- 问题：`Start Session` 后右侧 Gallery 不显示标注图，终端提示返回值数量多于 outputs。
- 原因：`demo.py` 中 `start_session` 和 `stop_session` 返回 10 个值，但 Gradio 事件只绑定了 9 个输出。
- 处理：删除多余返回值，使返回值数量与 outputs 对齐。

- 问题：模拟器出现 `System UI isn't responding` 弹窗。
- 原因：当前无 KVM 的软件模拟器运行较慢，系统 UI 偶发无响应。
- 处理：在人工探索中点击 `Wait`，页面恢复后继续低风险操作。

- 问题：`swipe` 动作的方向控件没有稳定显示。
- 原因：Gradio 动态控件在当前页面状态下未刷新出 `swipe_direction`。
- 处理：本次演示改用 `tap` 完成多步低风险人工探索；后续如需稳定 swipe，可单独修复控件显示逻辑。

- 结果：Gradio Demo 可访问，`emulator-5554` 初始化成功，人工探索能截图、解析、执行多步动作并生成状态 JSON；第 6 步最小验证通过。

## 后续处理建议

1. 后续入库前先确认 Neo4j 与 Pinecone 连通性仍通过，再点击 `Store Record to Database`。
2. 若继续人工探索演示，优先选择 Settings 中低风险页面和 `tap` 动作。
3. 如需展示自动探索，应另开步骤处理最大步数、超时和失败回退，避免长流程不可控。
