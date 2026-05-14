# AppAgentX 实验记录

## 记录范围

本文件只记录 AppAgentX 复现与评测所需的实验结果。架构说明、执行计划、服务申请步骤、密钥、本地私有路径和未验证推断不写入本文件。

## 当前结果状态

截至 2026-05-13，`memory-bank/architecture.md` 与 `memory-bank/plan.md` 中未记录任何已完成的正式实验结果。当前仓库也未确认包含可直接复现实验结果的示例状态 JSON、Neo4j dump 或 benchmark 任务集。

因此，本文件当前不记录成功率、耗时、步数、命中率等数值指标；这些指标必须在实际运行后补充。

## 必要实验记录项

| 实验 ID | 模块 | 目标 | 必要输入 | 必要指标 | 当前状态 | 结果摘要 |
| --- | --- | --- | --- | --- | --- | --- |
| EXP-ENV-001 | 环境准备 | 验证 `.venv` 与主依赖可用 | `.venv`、`AppAgentX/requirements.txt` | Python 版本、核心依赖 import 状态、CUDA 状态 | 已完成 | 主依赖、本地模块导入通过；CUDA 可用，7 张 GPU |
| EXP-CRED-001 | 凭据准备 | 验证外部服务凭据字段已准备 | 仓库外 `credentials.env` | 文件权限、字段完整性、基础格式、仓库外位置 | 已完成 | LLM、Neo4j、Pinecone 必要字段通过本地脚本验证 |
| EXP-CONFIG-001 | 配置连通性 | 验证 `config.py` 可加载凭据并连接外部服务 | `config.py`、仓库外 `credentials.env` | LLM 请求、Neo4j connectivity、Pinecone connectivity | 已完成 | 三项服务连通性均通过 |
| EXP-SVC-001 | 后端服务 | 验证 OmniParser 与 ImageEmbedding 服务可用 | 本地 uvicorn 服务、模型权重、GPU/CPU 环境 | 服务状态、接口返回状态、特征维度 | 已完成 | 本地非 Docker 模式下两个 backend 服务通过验证 |
| EXP-ADB-001 | 设备连接 | 验证 Android 设备或模拟器可操作 | ADB 设备 ID | 设备状态、屏幕尺寸、截图成功状态 | 已完成 | Android emulator 在线；屏幕尺寸和截图验证通过 |
| EXP-TRACE-001 | 轨迹采集 | 生成一条最小人工或自动探索轨迹 | 任务描述、设备、OmniParser 服务 | 步数、截图数量、状态 JSON 路径、异常数 | 已完成 | Demo 人工探索生成状态 JSON，通过最小验证 |
| EXP-DB-001 | 轨迹入库 | 验证状态 JSON 可写入 Neo4j 与 Pinecone | `state_*.json`、Neo4j、Pinecone | Page 数、Element 数、关系数、向量写入数 | 未记录 | 待实际执行后补充 |
| EXP-CHAIN-001 | 链理解 | 验证操作链可被读取、理解并写回图数据库 | 起始 `page_id`、LLM、Neo4j | 三元组数量、处理成功数、JSON 解析失败数、写回成功数 | 未记录 | 待实际执行后补充 |
| EXP-EVOLVE-001 | 链进化 | 验证低级操作链可生成高阶 Action 节点 | 起始 `page_id`、LLM、Neo4j | 模板化判断、Action 节点数、COMPOSED_OF 关系数 | 未记录 | 待实际执行后补充 |
| EXP-DEPLOY-001 | 部署执行 | 验证高阶动作可用于相似任务执行 | 用户任务、设备、Action 节点、后端服务 | 高阶动作命中状态、执行成功状态、回退状态、总步数、耗时 | 未记录 | 待实际执行后补充 |

## 单次实验记录格式

| 字段 | 内容 |
| --- | --- |
| 实验 ID | 使用上表 ID，必要时追加日期或序号 |
| 日期 | `YYYY-MM-DD` |
| 代码版本 | Git commit 或 `git status --short` 摘要 |
| 环境 | Python、CUDA、设备、后端服务状态 |
| 输入 | 任务描述、状态 JSON、起始 `page_id` 或 Action ID |
| 指标 | 只记录本次实验实际产生的指标 |
| 结果 | 成功、失败或部分成功 |
| 失败原因 | 若失败，记录可复查的错误摘要 |
| 备注 | 只写影响复现或评测解释的必要信息 |

## 已完成实验记录

### EXP-ENV-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-ENV-001 |
| 日期 | 2026-05-13 |
| 代码版本 | 工作区存在 `memory-bank/plan.md` 文档改动；未出现 `AppAgentX/` 源码改动 |
| 环境 | Python 3.10.12 虚拟环境；`torch 2.11.0+cu130`；CUDA 可用；GPU 数量 7；Docker 路径 `/usr/bin/docker` |
| 输入 | `.venv`、`AppAgentX/requirements.txt` |
| 指标 | 核心依赖 import 成功；本地模块 import 成功；`adb` 未检测到 |
| 结果 | 成功 |
| 失败原因 | 无；`python3 -m venv .venv` 因缺少 `ensurepip` 失败，已用 `python3 -m virtualenv .venv` 完成 |
| 备注 | 第 1 步不配置 Key、不启动 Docker、不连接手机；`adb` 缺失留到第 5 步处理 |

### EXP-CRED-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-CRED-001 |
| 日期 | 2026-05-13 |
| 代码版本 | 工作区存在 memory-bank 文档改动和新增 `scripts/verify-step2-credentials.sh`；未修改 `AppAgentX/config.py` |
| 环境 | 仓库外凭据文件 `/home/tiger/.config/appagentx/credentials.env`；权限 `600` |
| 输入 | LLM、Neo4j、Pinecone 的本地凭据字段 |
| 指标 | 字段完整；LLM base URL 为 HTTPS；Neo4j URI 前缀合法；Pinecone 区域为 `us-east-1`；凭据文件位于仓库外 |
| 结果 | 成功 |
| 失败原因 | 无 |
| 备注 | 未记录真实 Key、密码或完整 URI；第 3 步再配置 `AppAgentX/config.py` |

### EXP-CONFIG-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-CONFIG-001 |
| 日期 | 2026-05-13 |
| 代码版本 | 修改 `AppAgentX/config.py`、`AppAgentX/requirements.txt`，新增/更新验证脚本；未启动第 4 步服务 |
| 环境 | `.venv`；仓库外 `credentials.env`；DeepSeek OpenAI-compatible API；Neo4j Aura；Pinecone |
| 输入 | `scripts/verify-step3-config.py`、`AppAgentX/config.py` |
| 指标 | LLM 最小请求成功；Neo4j connectivity 成功；Pinecone connectivity 成功 |
| 结果 | 成功 |
| 失败原因 | 中间失败已解决：本地代理端口未运行导致 LLM 连接拒绝；Neo4j Aura 原 URI routing 失败，改用 `neo4j+s://` 后通过 |
| 备注 | 未记录真实 Key、密码或完整 URI；第 4 步仍未开始 |

### EXP-SVC-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-SVC-001 |
| 日期 | 2026-05-14 |
| 代码版本 | 修改 OmniParser 本地兼容逻辑和后端验证脚本；权重目录为本地运行产物，不应提交大文件 |
| 环境 | `.venv`；ImageEmbedding `127.0.0.1:8001`；OmniParser `127.0.0.1:8000`；本地非 Docker 替代方案 |
| 输入 | `scripts/verify-step4-backend.py`、OmniParser 权重、测试截图 |
| 指标 | ImageEmbedding 特征 shape `[1, 2048]`；OmniParser 返回元素数 `2`；OmniParser 耗时约 `4.42s` |
| 结果 | 成功 |
| 失败原因 | 中间失败已解决：当前容器不支持 Docker build/pull 所需 mount/unshare；OmniParser 依赖存在 NumPy、Transformers、Ultralytics、PaddleOCR 兼容问题 |
| 备注 | PaddleOCR 在当前环境降级为失败时跳过 OCR 文本框；本次验证仍通过 YOLO + Florence 返回界面元素 |

### EXP-ADB-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-ADB-001 |
| 日期 | 2026-05-14 |
| 代码版本 | 新增/更新 `scripts/verify-step5-adb.py`；修复 `AppAgentX/tool/screen_content.py` 截图回退路径 |
| 环境 | `.venv`；Android SDK 位于 `/home/tiger/android-sdk`；AVD `appagentx_api36`；设备 ID `emulator-5554` |
| 输入 | `scripts/verify-step5-adb.py`、Android emulator |
| 指标 | 设备状态 `device`；屏幕尺寸 `1080x1920`；项目工具尺寸匹配；截图尺寸 `1080x1920` |
| 结果 | 成功 |
| 失败原因 | 中间失败已解决：初始无 `adb` 和在线设备；当前环境无 `/dev/kvm`，使用 `-accel off`；`/sdcard` 截图写入失败后改用 `/data/local/tmp` 回退路径 |
| 备注 | 截图保存到 `log/step5_screenshots/step5_adb/`；第 5 步不运行 Demo 或 Agent |

### EXP-TRACE-001

| 字段 | 内容 |
| --- | --- |
| 实验 ID | EXP-TRACE-001 |
| 日期 | 2026-05-14 |
| 代码版本 | 修复 `AppAgentX/demo.py` 人工探索按钮返回值数量；依赖环境中恢复新版 OpenAI SDK 与 LangChain 0.3 系列兼容组合 |
| 环境 | `.venv`；Gradio Demo `7860`；OmniParser `127.0.0.1:8000`；ImageEmbedding `127.0.0.1:8001`；ADB 设备 `emulator-5554` |
| 输入 | 任务 `Open Android Settings and record one safe manual exploration step.`；Android Settings 页面；人工探索动作 |
| 指标 | Demo 可访问；设备初始化成功；人工探索截图和解析成功；状态 JSON 生成；验证脚本输出 `step6_demo_minimal_ok` |
| 结果 | 成功 |
| 失败原因 | 中间失败已解决：backend 需重启；`openai==1.3.5` 与 `langchain-openai` 不兼容；LangChain 1.x 移除旧 `langchain.prompts` 路径；Gradio 回调返回值数量多于 outputs |
| 备注 | 本次只验证轨迹采集闭环；未点击 `Store Record to Database`，未运行自动探索、链理解、链进化和 Action Execution |
