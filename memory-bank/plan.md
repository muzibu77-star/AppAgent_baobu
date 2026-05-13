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
进 backend/ 目录按其 README 用 Docker 拉起屏幕识别/特征提取服务（需要 GPU，没 GPU 就先试 CPU 镜像或换成调用 OmniParser 在线版）。
5. 连接 Android 设备
装好 ADB，物理机开 USB 调试连数据线，或者用 Android Studio 的模拟器，adb devices 能看到设备即可。
6. 运行 Demo
python demo.py 启动 Gradio，浏览器打开界面跑一个简单任务（比如打开某个 app）做端到端验证。
