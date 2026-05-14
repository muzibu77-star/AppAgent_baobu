1. 环境准备
本步骤只做本地 Python 环境与基础依赖准备，不配置 Key、不修改 `config.py`、不启动 Docker、不连接手机。
  - 确认当前位置与项目结构：当前路径应为仓库根目录；`AppAgentX/`、`memory-bank/`、`AppAgentX/backend/`、`AppAgentX/requirements.txt` 都应存在。
  - 确认架构文档已就位：`memory-bank/architecture.md` 应存在，并能看到 `# AppAgentX 架构说明` 标题。
  - 检查 Git 工作区状态：记录当前已有改动；本步骤结束后不应新增或修改 AppAgentX 源码文件。
  - 创建或复用仓库根目录 `.venv`：优先使用 `.venv`，不使用 conda；验证 `.venv/bin/python` 存在，并能输出 Python 版本。
  - 安装 AppAgentX 主依赖：使用 `.venv` 安装 `AppAgentX/requirements.txt`；验证安装过程无 error。
  - 验证核心依赖可用：用 `.venv` 导入 `gradio`、`neo4j`、`langchain`、`langgraph`、`langchain_openai`、`torch`、`PIL`，预期全部成功。
  - 验证本地模块可导入：在 `AppAgentX/` 目录下导入 `config`、`data.State`、`tool.screen_content`，预期全部成功；只做导入，不连接外部服务。
  - 记录后续外部依赖是否具备：只检查 Docker 配置、backend 入口文件、OmniParser 权重目录、ADB 命令是否存在；缺失项记录到后续步骤，不阻塞第一步完成。
  - 做最终环境确认：`.venv` 可用、主依赖可导入、本地模块可导入；`git status` 不应出现因环境准备导致的源码变更。
2. 申请外部服务的 Key
本步骤只申请并确认 AppAgentX 需要的外部服务凭据，不修改 `config.py`，不把 Key 写入仓库，不启动 Demo，不连接后端服务。
  - 确认服务清单：必须包含 Neo4j、Pinecone、LLM 三项；LangSmith 只作为可选项，不阻塞复现。
  - 准备本地保密记录位置：记录位置必须在当前 Git 仓库外；验证不会被提交，且能保存服务名称、账号、URL、Key、备注。
  - 注册或登录 Neo4j：优先使用 Aura 免费实例；验证能进入控制台，账号状态正常，且可创建数据库实例。
  - 创建 Neo4j 数据库实例：验证实例状态为可用或运行中，并能看到连接 URI、用户名和密码。
  - 记录 Neo4j 连接信息：本地保密记录中应包含 URI、用户名、密码；URI 格式应适配 Neo4j Python driver。
  - 注册或登录 Pinecone：验证能进入控制台，账号状态正常，免费额度或可用额度满足创建索引。
  - 创建或确认 Pinecone API Key：验证 Key 状态为启用，归属项目与本次 AppAgentX 复现一致。
  - 确认 Pinecone 区域兼容性：优先确认 serverless 和 AWS us-east-1 可用，因为当前代码默认按该区域创建索引。
  - 记录 Pinecone 信息：本地保密记录中应包含 API Key、项目名、区域；不得写入 `plan.md` 或 `config.py`。
  - 选择 LLM 服务商：默认使用 DeepSeek 的 OpenAI 兼容接口；如改用 OpenAI 或其他兼容服务，必须能提供 base URL、API Key、模型名。
  - 创建 LLM API Key：验证 Key 状态为启用，账号余额或免费额度可支持少量测试请求。
  - 确认 LLM 模型名和 base URL：DeepSeek 默认记录 `deepseek-chat`；验证 base URL 不为空，且来自服务商文档或控制台。
  - 做供应商侧连通性确认：Neo4j 实例健康、Pinecone Key 可用、LLM 控制台或 Playground 能完成最小测试；无法测试时记录为第 3 步配置后验证。
  - 汇总第 3 步待配置字段：本地保密记录至少包含 LLM base URL、LLM API Key、LLM model、Neo4j URI、Neo4j 用户名、Neo4j 密码、Pinecone API Key。
  - 做安全检查：Key 不应出现在聊天记录、`plan.md`、`architecture.md`、`config.py` 或任何仓库文件中。
  - 做最终状态确认：本步骤只产生仓库外本地保密记录；`git status` 不应因为申请 Key 出现新的代码或配置变更。
3. 配置 config.py
本步骤把第 2 步获得的 Neo4j、Pinecone、LLM 凭据填入 `AppAgentX/config.py`，并做最小连通性验证；不启动 backend 容器，不连接手机，不运行 Demo。
  - 确认配置文件位置：`AppAgentX/config.py` 应存在，并包含 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`、`Neo4j_URI`、`Neo4j_AUTH`、`PINECONE_API_KEY` 字段。
  - 确认本地保密记录完整：仓库外记录中应已有 LLM base URL、LLM API Key、LLM model、Neo4j URI、Neo4j 用户名、Neo4j 密码、Pinecone API Key。
  - 记录修改前 Git 状态：明确当前已有改动；确认后续 `config.py` 修改只作为本地复现配置，不提交。
  - 配置 LLM 连接信息：`LLM_BASE_URL` 应非空，`LLM_API_KEY` 应非占位值，`LLM_MODEL` 应为实际可用模型；DeepSeek 默认使用 `deepseek-chat`。
  - 保留 LLM 请求参数默认值：`LLM_MAX_TOKEN`、`LLM_REQUEST_TIMEOUT`、`LLM_MAX_RETRIES` 保持可用数值；除非请求失败，不提前调整。
  - 配置 Neo4j 连接信息：`Neo4j_URI` 应与第 2 步记录一致；`Neo4j_AUTH` 中用户名和密码应非占位值。
  - 配置 Pinecone Key：`PINECONE_API_KEY` 应非占位值；Key 应与第 2 步记录的 Pinecone 项目一致。
  - 暂不修改 backend 服务地址：`Feature_URI` 保持 `http://127.0.0.1:8001`，`Omni_URI` 保持 `http://127.0.0.1:8000`；这两个服务在第 4 步启动后再验证。
  - 暂不启用 LangSmith：`LANGCHAIN_TRACING_V2` 保持 `false`；`LANGCHAIN_API_KEY` 即使仍是占位值也不影响本步骤。
  - 检查配置文件可被导入：在 `AppAgentX/` 目录下用 `.venv` 导入 `config` 成功；不应触发外部服务连接。
  - 验证 LLM 最小请求：用 `.venv` 发起一次极短 LLM 调用；预期返回正常文本，不出现鉴权失败、模型不存在或 base URL 错误。
  - 验证 Neo4j 最小连接：用 `.venv` 建立 Neo4j driver 连接并执行连通性检查；预期连接成功，无认证错误。
  - 验证 Pinecone 最小连接：用 `.venv` 初始化 Pinecone client 并读取项目或索引状态；预期 API Key 有效，无权限错误。
  - 记录无法通过的服务：若任一服务失败，记录服务名、错误摘要、疑似原因；不要继续伪造占位值。
  - 做安全检查：真实 Key 不应出现在 `plan.md`、`architecture.md`、聊天记录或其他文档中；`config.py` 的真实 Key 仅作为本地临时配置。
  - 做最终状态确认：`config.py` 可能显示为本地修改；除 `config.py` 外，不应因为本步骤修改 AppAgentX 源码或文档。
4. 启动 backend 容器
本步骤负责启动 AppAgentX 的两个 backend 服务：Image Feature Extraction 服务和 OmniParser Screen Parsing 服务；不运行 Gradio，不连接手机，不执行 Agent 任务。
  - 确认 backend 目录结构：验证 `AppAgentX/backend/` 下存在 `docker-compose.yml`、`ImageEmbedding/`、`OmniParser/`。
  - 确认服务入口文件：验证 `ImageEmbedding/image_embedding.py` 和 `OmniParser/omni.py` 存在。
  - 确认构建文件：验证两个服务的 `Dockerfile` 和 `requirements.txt` 都存在且非空。
  - 确认 compose 服务与端口：验证服务名为 `image-embedding`、`omni-parser`，端口分别为 `8001`、`8000`。
  - 检查 Docker 与 Compose：验证 Docker daemon 可用，Compose 能识别 backend 的 compose 文件。
  - 检查 GPU 容器支持：验证 NVIDIA GPU 与 Docker GPU runtime 可用；若不可用，记录为阻塞项。
  - 检查 OmniParser 权重：验证 `icon_detect_v1_5/best.pt` 和 `icon_caption_florence/` 存在；缺失则先补齐权重。
  - 确认端口未被占用：验证本机 `8000` 和 `8001` 空闲；如冲突，记录占用进程。
  - 构建并启动容器：验证两个镜像构建成功，两个容器启动成功，无依赖、权重或 GPU runtime 错误。
  - 检查容器状态：验证两个服务均处于运行状态；若退出，查看日志并记录首个明确错误。
  - 验证 ImageEmbedding：访问 `8001/available_models` 返回模型列表；设置 `resnet50` 后模型信息可读取。
  - 验证 OmniParser：提交一张有效测试图片到 `8000/process_image/`，返回 `status=success`、`parsed_content`、`labeled_image`、`e_time`。
  - 验证特征提取：提交同一测试图片到 `8001/extract_single/`，返回 `features`、`shape`、`model_name`、`time_taken`。
  - 对齐 `config.py` 默认地址：验证 `Feature_URI` 为 `http://127.0.0.1:8001`，`Omni_URI` 为 `http://127.0.0.1:8000`。
  - 最终确认：两个容器运行中，两个端口可访问，解析服务和特征服务均通过最小测试；不应修改 AppAgentX 源码。
5. 连接 Android 设备
本步骤负责让 AppAgentX 能通过 ADB 识别并操作一台 Android 真机或模拟器；只做设备连接、授权、基础状态检查和最小 ADB 验证，不运行 Gradio，不执行 Agent 任务。
  - 确认 ADB 已安装：验证系统能识别 ADB 工具，并能显示 ADB 版本信息。
  - 启动 ADB 服务：验证 ADB 服务处于运行状态；没有提示 daemon 启动失败或权限错误。
  - 选择设备类型：若使用真机，应准备 USB 数据线并开启开发者选项；若使用模拟器，应先启动 Android Studio 模拟器。
  - 真机开启 USB 调试：验证手机开发者选项中 USB 调试已开启；连接电脑后手机弹出授权提示。
  - 真机完成电脑授权：验证手机上允许当前电脑调试；ADB 设备列表中该设备状态不应是 `unauthorized`。
  - 模拟器启动完成：验证 Android 模拟器进入系统桌面；不是黑屏、启动动画或离线状态。
  - 检查设备列表：验证 ADB 设备列表中至少出现一台状态为 `device` 的设备或模拟器。
  - 处理多设备情况：若设备列表中有多台设备，明确选择一个目标 device id；后续所有操作都使用该 id。
  - 记录目标设备 id：本地记录中保存目标设备 id；该 id 与 ADB 设备列表完全一致。
  - 检查设备在线状态：目标设备状态应为 `device`；不应是 `offline`、`unauthorized` 或空白。
  - 唤醒并解锁设备：验证设备屏幕处于亮屏、解锁状态；当前页面可被截图，不停留在锁屏密码页。
  - 确认设备屏幕尺寸可读取：ADB 能读取目标设备分辨率；返回宽度和高度两个有效数值。
  - 确认项目工具可读取设备列表：AppAgentX 的设备枚举逻辑能看到同一个目标 device id。
  - 确认项目工具可读取屏幕尺寸：AppAgentX 的屏幕尺寸读取逻辑返回宽度和高度；结果与 ADB 读取结果一致或接近。
  - 做一次最小截图验证：目标设备能成功生成截图并拉取到本地；截图文件存在且能打开。
  - 检查目标 App 是否可用：复现任务需要操作的 App 已安装；若未安装，记录为第 6 步运行 Demo 前的阻塞项。
  - 保持设备环境稳定：验证设备不自动锁屏、网络可用、电量充足或已连接电源。
  - 做最终连接确认：目标 device id 已记录，设备在线，屏幕尺寸可读，截图可用；不应修改 AppAgentX 源码或配置文件。
6. 运行 Demo
python demo.py 启动 Gradio，浏览器打开界面跑一个简单任务（比如打开某个 app）做端到端验证。
本步骤负责启动 AppAgentX 的 Gradio Demo，并完成一次最小端到端验证。验证范围包括页面启动、设备刷新、任务初始化、截图解析、人工探索生成记录、记录入库前检查；不做长任务，不做批量实验。

执行步骤
确认前置步骤已完成
验证：.venv 可用，config.py 已配置，backend 两个服务可访问，ADB 目标设备在线。

确认运行目录
验证：当前目录切换到 AppAgentX/；目录中应存在 demo.py、config.py、requirements.txt。

确认 Demo 入口存在
验证：demo.py 文件存在，并包含 Gradio 启动入口。

确认 Python 环境一致
验证：运行 Demo 时使用仓库根目录 .venv 的 Python；不使用系统全局 Python。

启动 Demo 服务
验证：终端显示 Gradio 服务已启动，并给出本地访问地址；启动过程无 import error。

打开 Gradio 页面
验证：浏览器能访问 Demo 地址；页面能看到 Initialization、Auto Exploration、User Exploration、Chain Understanding & Evolution、Action Execution 等页签。

刷新设备列表
验证：Initialization 页点击刷新后，设备列表中出现第 5 步记录的目标 device id；不应显示 No devices found。

输入最小测试任务
验证：任务文本框中填入一个简单、低风险、可观察的任务；任务不涉及登录、支付、删除或隐私数据。

初始化设备和任务
验证：点击初始化后，页面返回目标 device id 和任务信息；不应出现设备无效或任务为空错误。

进入人工探索页
验证：User Exploration 页可见 Start Session 按钮；初始化后该流程可启动。

启动人工探索会话
验证：点击 Start Session 后能触发截图和页面解析；截图区域出现标注后的页面图或日志中出现解析结果。

检查截图产物
验证：本地 log/screenshots 下出现当前任务相关截图；截图文件能打开且内容不是空白。

检查解析产物
验证：截图目录下出现 processed images 和元素 JSON；JSON 中应包含界面元素列表。

执行一个低风险人工动作
验证：选择一个清晰元素执行 tap 或 swipe；页面日志记录本次动作，设备界面有可观察变化。

停止人工探索会话
验证：点击 Stop Session 后状态 JSON 被保存；日志中出现保存路径或保存成功提示。

检查状态 JSON
验证：log/json_state 中出现新的状态文件；文件包含任务描述、应用名、步数、历史步骤和最终页面信息。

刷新链理解文件列表
验证：Chain Understanding & Evolution 页刷新后能看到刚生成的 JSON 文件；文件详情能显示任务描述和步数。

暂不执行入库和链进化
验证：本轮最小 Demo 验证到文件可见即可；若要点击 Store Record to Database，必须先确认 Neo4j 和 Pinecone 已通过第 3 步验证。

检查自动探索入口可用性
验证：Auto Exploration 页能看到 Start Exploration 按钮；本步骤不默认启动自动探索，避免长时间或不可控操作。

检查 Action Execution 页可见性
验证：Action Execution 页能打开，并能刷新设备列表；本步骤不执行高阶动作部署任务。

关闭 Demo 服务
验证：终端进程停止后，本地 Gradio 地址不再可访问；无残留后台进程占用端口。

做最终状态确认
验证：Demo 能启动，设备能初始化，人工探索能截图解析，状态 JSON 能生成；除运行日志和截图产物外，不应修改 AppAgentX 源码。

测试计划
通过标准：Gradio 页面可访问，目标设备可刷新，初始化成功，人工探索能生成截图、解析 JSON 和状态 JSON。
阻塞项：Demo import 失败、Gradio 端口占用、设备列表为空、backend 服务不可用、截图失败、OmniParser 解析失败。
失败处理：import 失败先查依赖；端口占用先换端口或停止旧服务；设备为空回到第 5 步；解析失败回到第 4 步；配置错误回到第 3 步。
默认选择
默认使用人工探索做最小端到端验证。
默认不启动自动探索，避免不可控多步操作。
默认不在第 6 步执行链理解、链进化或高阶动作部署。
默认测试任务选择低风险、可观察、无需登录的手机操作。