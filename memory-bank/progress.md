# AppAgentX 复现进度

## 2026-05-13：第 1 步环境准备

- 已确认仓库根目录为 `/home/tiger/BaoBuu/AppAgent_baobu`，关键目录与文件存在：`AppAgentX/`、`memory-bank/`、`AppAgentX/backend/`、`AppAgentX/requirements.txt`、`memory-bank/architecture.md`。
- `python3 -m venv .venv` 因系统缺少 `ensurepip` 失败，已改用 `python3 -m virtualenv .venv` 创建仓库根目录虚拟环境。
- 已安装 `AppAgentX/requirements.txt` 主依赖。
- 已验证核心依赖可导入：`gradio`、`neo4j`、`langchain`、`langgraph`、`langchain_openai`、`torch`、`PIL`。
- 已验证本地模块可导入：`config`、`data.State`、`tool.screen_content`。
- CUDA 可用，`torch` 版本为 `2.11.0+cu130`，检测到 7 张 GPU。
- Docker 可用，路径为 `/usr/bin/docker`；`adb` 未检测到，不阻塞第 1 步。
- 第 1 步未修改 `AppAgentX/` 源码；当前工作区显示 `memory-bank/plan.md` 有既有文档改动。

## 2026-05-13：第 2 步外部服务凭据准备

- 已在仓库外使用 `/home/tiger/.config/appagentx/credentials.env` 保存复现所需凭据字段。
- 已新增 `scripts/verify-step2-credentials.sh`，用于验证凭据文件存在、权限为 `600`、字段完整、基础格式正确，并确认凭据文件不在仓库内。
- 已验证必需字段存在：LLM base URL、LLM model、LLM API key、Neo4j URI、Neo4j 用户名、Neo4j 密码、Pinecone API key、Pinecone 项目、Pinecone 区域。
- 已验证 LLM base URL 使用 `https://`，Neo4j URI 前缀合法，Pinecone 区域为 `us-east-1`。
- 本步骤未修改 `AppAgentX/config.py`，未启动 Docker，未连接手机，未运行 Demo。

## 2026-05-13：第 3 步配置与连通性验证

- 已更新 `AppAgentX/config.py`，从仓库外 `/home/tiger/.config/appagentx/credentials.env` 加载 LLM、Neo4j、Pinecone 配置；未把真实 Key 写入仓库。
- 已新增 `scripts/verify-step3-config.py`，用于验证配置导入、LLM 最小请求、Neo4j 连通性和 Pinecone 连通性。
- 已在 `AppAgentX/requirements.txt` 补充 `pinecone`，因为 `AppAgentX/data/vector_db.py` 运行时依赖 Pinecone SDK。
- 初次验证发现本机代理 `127.0.0.1:7890` 未运行，LLM 请求连接被拒绝；验证脚本已改为忽略环境代理。
- 初次 Neo4j 验证失败于 routing 信息获取；TCP 直连 `7687` 端口正常，改用 Aura 安全 URI `neo4j+s://...` 后通过。
- 最终验证通过：`llm_request_ok`、`neo4j_connectivity_ok`、`pinecone_connectivity_ok`、`step3_config_services_ok`。
- 本步骤未启动 backend 容器，未连接手机，未运行 Demo。

## 2026-05-14：第 4 步 backend 服务验证

- 当前容器环境无法完成 Docker 构建和镜像解包，表现为 Docker daemon、iptables、BuildKit mount、`unshare` 权限问题；第 4 步改用本地非 Docker 替代方案。
- 已用 `.venv` 直接启动两个 FastAPI 服务：ImageEmbedding 监听 `8001`，OmniParser 监听 `8000`。
- 已准备 OmniParser 权重：`weights/icon_detect_v1_5/best.pt` 和 `weights/icon_caption_florence/`。
- 已新增/使用 `scripts/verify-step4-backend.py` 验证 backend 预检、端口连通、ImageEmbedding 特征提取和 OmniParser 图片解析。
- 已为 OmniParser 本地运行做兼容修复：`flash_attn` 静态导入占位、EasyOCR/PaddleOCR lazy 初始化、PaddleOCR 3.x 参数适配、PaddleOCR 失败时降级跳过 OCR 文本框、空 OCR 框结构统一。
- 最终验证通过：`image_embedding_shape [1, 2048]`、`omni_parser_process_image_ok`、`omni_parser_elements 2`、`step4_backend_services_ok`。
- 本步骤未连接 Android 设备，未运行 Gradio Demo；第 5 步仍需单独验证 ADB 和设备连接。

## 2026-05-14：第 5 步 ADB 设备连接验证

- 已新增 `scripts/verify-step5-adb.py`，用于验证 ADB 可用性、设备在线状态、屏幕尺寸、项目屏幕工具和最小截图。
- 初始环境缺少 `adb`，后续安装 Android SDK Platform Tools，并使用 `/home/tiger/android-sdk/platform-tools/adb`。
- 因没有真实 Android 设备，已安装 Android SDK Command-Line Tools、Emulator、Android 36 system image，并创建 `appagentx_api36` AVD。
- 当前环境没有 `/dev/kvm`，模拟器以 `-accel off` 无窗口模式运行；启动较慢但可用于第 5 步验证。
- 已修复 `scripts/verify-step5-adb.py`，让验证脚本优先使用 Android SDK 的 `adb`，避免系统旧版 ADB 与 SDK emulator 混用。
- 已修复 `AppAgentX/tool/screen_content.py` 的截图工具：当 `/sdcard` 写入失败时，自动回退到 `/data/local/tmp`。
- 最终验证通过：目标设备为 `emulator-5554`，屏幕尺寸 `1080x1920`，项目工具尺寸匹配，截图保存成功，输出 `step5_adb_device_ok`。
- 本步骤未运行 Gradio Demo，未执行自动探索、人工探索或 Agent 任务。

## 2026-05-14：第 6 步 Demo 最小端到端验证

- 已启动 Gradio Demo，并通过 VS Code 端口转发访问 `7860`。
- 已在 `Initialization` 页刷新到 `emulator-5554`，并完成任务初始化。
- 已在 `User Exploration` 页启动人工探索，会话能截图、调用 OmniParser 解析并显示标注图。
- 已执行多步低风险人工动作，页面显示动作记录，验证人工探索链路可写入 `history_steps`。
- 已点击 `Stop Session` 保存状态 JSON，并确认验证脚本输出通过。
- 为完成本步骤，已修复 `AppAgentX/demo.py` 中 `start_session` / `stop_session` 返回值数量与 Gradio outputs 不一致的问题。
- 第 6 步只验证到 Demo 启动、设备初始化、人工探索、截图解析和状态 JSON 生成；未执行自动探索、入库、链理解、链进化或部署执行。
