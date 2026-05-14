# AppAgentX 架构说明

## 1. 方案概述

本方案名称为 AppAgentX 复现，原始项目位于本仓库的 `AppAgentX/` 目录。该项目面向手机 GUI Agent，目标是让智能体在 Android 设备或模拟器上完成用户任务，并把任务执行过程记录为可复用的操作链。项目已有能力包括：通过 ADB 截屏和执行屏幕操作，通过 OmniParser 服务解析界面元素，通过 LangChain/LangGraph 驱动 LLM 决策，通过 Neo4j 保存页面、元素和操作关系，通过 Pinecone 保存元素视觉向量，并把低级操作链进一步理解和进化为高阶动作。

当前复现工作的核心目标不是训练一个新模型，而是跑通 AppAgentX 的完整工程闭环：设备初始化、自动或人工探索、操作轨迹保存、轨迹入库、操作链理解、操作链进化、高阶动作部署执行。该工作与后续研究目标的关系在于：现有项目提供了 GUI Agent 记忆、操作链抽象和高阶动作复用的基础框架，后续可以在任务集、记忆检索、动作模板评测、失败回退策略和跨应用泛化上继续改造。

## 2. 涉及的核心模块

根据本方案的具体目标“复现 AppAgentX 并理解现有整体框架”，涉及的核心模块如下：

1. **Gradio 入口与交互界面（`AppAgentX/demo.py`）**
   - 作用：提供初始化、自动探索、人工探索、链理解与进化、高阶动作执行五类交互入口。
   - 为什么需要：复现时多数流程从该文件触发，是串联设备、探索、数据库和部署执行的主入口。
   - 在本方案中的改造方向：优先保持原结构，后续可补充更清晰的状态提示、异常提示和复现实验日志导出。

2. **自动探索智能体（`AppAgentX/explor_auto.py`）**
   - 作用：用 LangGraph 定义自动探索状态图，由 LLM 观察页面、选择动作并循环执行。
   - 为什么需要：它生成可入库的历史操作轨迹，是链理解和高阶动作进化的数据来源。
   - 在本方案中的改造方向：复现阶段先跑通；后续可加入最大步数、任务完成判定修正和失败类型统计。

3. **人工探索模块（`AppAgentX/explor_human.py`）**
   - 作用：允许用户按元素编号执行 tap、text、swipe、long press 等动作，并同步记录页面和操作历史。
   - 为什么需要：自动探索不稳定时，可用人工探索生成高质量示范轨迹。
   - 在本方案中的改造方向：优先作为人工数据采集入口；后续可修正动作命名不一致和元素坐标转换边界问题。

4. **状态与轨迹存储模块（`AppAgentX/data/State.py`、`AppAgentX/data/data_storage.py`）**
   - 作用：定义探索态和部署态，并把运行轨迹导出为 JSON，再写入 Neo4j 与 Pinecone。
   - 为什么需要：这是项目的记忆层入口，决定后续链理解能否拿到完整页面-元素-页面三元组。
   - 在本方案中的改造方向：复现时确认 JSON 字段完整性；后续可统一坐标、设备分辨率和最终页面时间戳。

5. **图数据库模块（`AppAgentX/data/graph_db.py`）**
   - 作用：封装 Neo4j 节点创建、关系创建、链查询和高阶动作查询。
   - 为什么需要：AppAgentX 的核心记忆结构依赖图数据库表达页面、元素、动作之间的关系。
   - 在本方案中的改造方向：复现时按现有 schema 使用；后续可补充唯一约束、索引、清理脚本和数据库迁移说明。

6. **向量数据库与视觉特征模块（`AppAgentX/data/vector_db.py`、`AppAgentX/tool/img_tool.py`）**
   - 作用：裁剪 UI 元素图像、调用特征服务提取向量，并写入 Pinecone。
   - 为什么需要：部署执行时需要把当前屏幕元素与历史模板元素进行匹配。
   - 在本方案中的改造方向：复现时确认特征服务、Pinecone API key 和索引维度一致；后续可替换本地向量库以降低外部依赖。

7. **屏幕工具模块（`AppAgentX/tool/screen_content.py`）**
   - 作用：封装 ADB 设备列表、屏幕尺寸、截图、界面元素解析和屏幕动作执行。
   - 为什么需要：这是智能体和真实 Android 环境交互的工具层。
   - 在本方案中的改造方向：复现时检查 ADB、设备 ID 和后端服务地址；后续可移除 `shell=True` 或增加命令白名单以提高安全性。

8. **链理解模块（`AppAgentX/chain_understand.py`）**
   - 作用：从 Neo4j 中取出页面-元素-页面三元组，调用 LLM 生成上下文、用户意图、状态变化等增强描述，并写回数据库。
   - 为什么需要：它把原始操作记录转换为可解释、可检索、可进化的语义操作链。
   - 在本方案中的改造方向：复现时先验证入库链可被读取；后续可固定输出 schema、增加失败重试和增量处理。

9. **链进化模块（`AppAgentX/chain_evolve.py`）**
   - 作用：评估操作链是否可模板化，并生成高阶 Action 节点及其元素序列关系。
   - 为什么需要：这是 AppAgentX “把重复低级操作进化为快捷高阶动作”的关键模块。
   - 在本方案中的改造方向：复现时验证 Action 节点创建；后续可加入模板质量评测、人工审核和版本管理。

10. **部署执行模块（`AppAgentX/deployment.py`）**
    - 作用：把用户任务匹配到高阶动作，尝试执行模板动作；失败时回退到 ReAct 基础操作。
    - 为什么需要：它验证链进化结果是否能真正用于新任务执行。
    - 在本方案中的改造方向：复现时关注高阶动作查询和回退链路；后续需要修正若干字段不一致问题，例如 `action_sequence` 与 `element_sequence` 的使用差异。

11. **后端解析与特征服务（`AppAgentX/backend/`）**
    - 作用：用 Docker 启动两个 FastAPI 服务：OmniParser 界面解析服务和 ImageEmbedding 特征提取服务。
    - 为什么需要：前者把截图变为 UI 元素 JSON 和标注图，后者为元素匹配提供视觉特征。
    - 在本方案中的改造方向：复现时按 README 准备权重和 GPU Docker 环境；后续可拆出服务健康检查脚本。

## 3. Gradio 入口与交互界面

### 3.1 解决的问题

`AppAgentX/demo.py` 解决的是复现流程入口分散的问题。它把设备初始化、自动探索、人工探索、轨迹入库、链理解、链进化和部署执行放在同一个 Gradio 应用中。主要函数包括 `initialize_device`、`auto_exploration`、`user_exploration`、`get_json_files`，以及界面内部的 `store_to_database`、`understand_chain`、`generate_high_level_action`、`execute_deployment_task`。

### 3.2 数据来源 / 输入格式

输入来自用户在 Gradio 界面中选择的 ADB 设备和任务描述。探索过程会生成截图、解析 JSON 和状态 JSON，默认保存在 `./log/screenshots` 和 `./log/json_state` 之下。该目录是运行时产物，本仓库当前没有提供固定示例数据。

### 3.3 训练方式 / 推理方式

该模块不训练模型。推理通过调用 `explor_auto.run_task`、`chain_understand.process_and_update_chain`、`chain_evolve.evolve_chain_to_action` 和 `deployment.run_task` 完成。LLM 配置来自 `AppAgentX/config.py`。

### 3.4 评测方式

复现阶段可以先用工程可运行性评测：能否列出 ADB 设备、能否截图、能否解析 UI 元素、能否生成状态 JSON、能否写入 Neo4j、能否生成高阶 Action 节点。后续实验可统计任务成功率、平均步骤数、平均耗时、高阶动作命中率、回退率和失败原因分布。

### 3.5 对当前方案的意义

该模块是复现起点。它把所有子模块串起来，适合先做端到端冒烟测试。需要注意的是，界面中存在若干临时逻辑，例如从文件名生成临时 task id、后台线程包装异步函数、部署执行时对 `deployment.run_task` 做临时替换。这些逻辑可以先用于复现，但不宜直接作为严谨实验脚本。

## 4. 自动探索智能体

### 4.1 解决的问题

`AppAgentX/explor_auto.py` 通过 LangGraph 构建自动探索流程。状态图节点包括 `tsk_setting`、`page_understand` 和 `perform_action`。流程从任务描述推断应用名，截屏并解析当前页面，再由 ReAct agent 基于截图、页面 JSON 和用户意图选择一个屏幕动作。

### 4.2 数据来源 / 输入格式

输入是 `State`，其中关键字段包括 `tsk`、`device`、`device_info`、`step`、`history_steps`、`page_history`、`current_page_screenshot`、`current_page_json`、`context` 和 `tool_results`。页面数据来自 ADB 截图和 OmniParser 输出的元素 JSON。

### 4.3 训练方式 / 推理方式

该模块不训练模型。推理方式是调用 OpenAI 兼容接口的 `ChatOpenAI`，并通过 `create_react_agent(model, [screen_action])` 执行动作。任务完成判定由 `tsk_completed` 通过 LLM 基于最近截图和任务完成标准判断。

### 4.4 评测方式

复现时应记录每个任务是否完成、执行步数、截图解析耗时、LLM 动作是否可执行、工具调用是否成功。严谨实验可增加成功率、平均动作数、任务完成判定准确率、异常终止率和与人工轨迹的动作重合度。

### 4.5 对当前方案的意义

自动探索是生成轨迹数据的主要方式。可复用代码包括 `run_task` 状态图、`perform_action` 的多模态提示构造、`screen_action` 工具调用和 `history_steps` 记录结构。复现时需要重点验证 LLM 配置、ADB 设备、OmniParser 服务三者是否同时可用。

## 5. 人工探索模块

### 5.1 解决的问题

`AppAgentX/explor_human.py` 解决人工示范采集问题。它先通过 `capture_and_parse_page` 捕获当前页面，再把界面元素编号映射成屏幕坐标，最后执行用户选择的动作并记录历史步骤。

### 5.2 数据来源 / 输入格式

输入是当前 `State`、动作类型、元素编号、文本输入或滑动方向。元素编号来自 OmniParser 解析 JSON 中的 `ID` 字段，坐标来自 `bbox` 相对坐标和 `device_info` 屏幕尺寸。

### 5.3 训练方式 / 推理方式

该模块不调用训练流程，也不依赖 LLM 决策。它通过规则方式把元素编号转换为坐标，再调用 ADB 工具执行动作。

### 5.4 评测方式

可评测每次人工动作是否成功、元素编号是否存在、坐标换算是否落在元素框内、动作后是否能成功截图和解析新页面。人工探索还可作为自动探索轨迹的对照数据。

### 5.5 对当前方案的意义

该模块适合在自动探索失败时生成可控轨迹。当前代码中 Gradio action 使用 `"long press"`，而 `single_human_explor` 支持的是 `"long_press"`，复现时需要注意动作名一致性，否则长按路径可能无法正常执行。

## 6. 状态与轨迹存储模块

### 6.1 解决的问题

`AppAgentX/data/State.py` 定义运行状态结构，`AppAgentX/data/data_storage.py` 负责把状态转为 JSON，再将操作轨迹写入 Neo4j 和 Pinecone。`state2json` 导出任务、历史步骤、应用名、步数和最终页面；`json2db` 把历史步骤转换为图数据库节点和关系。

### 6.2 数据来源 / 输入格式

`state2json` 输入是探索完成后的 `State` 字典。`json2db` 输入是 `./log/json_state/state_*.json` 文件。每条 `history_steps` 至少需要包含 `step`、`recommended_action`、`tool_result`、`source_page`、`source_json` 和 `timestamp`。

### 6.3 训练方式 / 推理方式

该模块不训练模型。它使用 Neo4j 保存结构化记忆，使用 Pinecone 保存元素视觉向量。元素视觉向量通过 `element2vector` 调用 `element_img` 裁剪元素，再通过 `extract_features(..., "resnet50")` 调用特征服务。

### 6.4 评测方式

可检查 JSON 是否成功生成，Neo4j 中 Page、Element 节点数量是否符合步数，`HAS_ELEMENT` 和 `LEADS_TO` 关系是否完整，Pinecone 中元素向量是否成功写入。也应检查异常日志中是否出现元素匹配失败、图片裁剪失败或向量写入失败。

### 6.5 对当前方案的意义

这是 AppAgentX 记忆机制的核心落点。后续所有链理解、链进化和部署执行都依赖这里写出的图结构。复现时应优先保证 `json2db` 在一条短人工轨迹上成功运行。

## 7. 数据库结构

### 7.1 Neo4j 节点

当前代码可确认的节点类型如下：

- `Page`：页面节点，关键属性包括 `page_id`、`description`、`raw_page_url`、`timestamp`、`elements`、`other_info`，部分逻辑还可能使用 `visual_embedding_id`。
- `Element`：元素节点，关键属性包括 `element_id`、`element_original_id`、`description`、`action_type`、`parameters`、`bounding_box`、`other_info`，部分逻辑还会写入 `reasoning`。
- `Action`：高阶动作节点，关键属性包括 `action_id`、`name`、`description`、`preconditions`、`element_sequence`、`template_pattern`、`is_high_level`。
- `Shortcut`：`graph_db.py` 中存在查询逻辑，但本仓库当前未看到创建 Shortcut 节点的代码；该部分需要根据后续运行数据或原项目补充确认。

### 7.2 Neo4j 关系

当前代码可确认的关系类型如下：

- `(Page)-[:HAS_ELEMENT]->(Element)`：表示某个页面包含某个可操作元素。
- `(Element)-[:LEADS_TO]->(Page)`：表示对元素执行某个动作后跳转到目标页面，关系属性包括 `action_name`、`action_params`、`confidence_score`。
- `(Action)-[:COMPOSED_OF]->(Element)`：表示高阶动作由一组元素操作组成，关系属性包括 `order`、`atomic_action`、`action_params`。
- `(Shortcut)-[:REFERS_TO]->(Action)`：存在读取逻辑，但创建逻辑当前无法确认。

### 7.3 Pinecone 向量结构

`VectorStore` 默认索引名为 `area-embedding`，维度为 2048，metric 为 cosine，namespace 按 `NodeType` 分为 `page` 和 `element`。当前写入逻辑主要写 `element` namespace。元素向量 metadata 包含 `original_id`、`bbox`、`type` 和 `content`。

### 7.4 数据流

复现时的主要数据流是：

1. ADB 截图生成页面图片。
2. OmniParser 将页面图片解析为元素 JSON 和标注图。
3. 自动或人工探索执行动作，并把动作、页面和工具结果写入 `State.history_steps`。
4. `state2json` 将状态保存为 `state_*.json`。
5. `json2db` 读取 JSON，创建 Page、Element、HAS_ELEMENT 和 LEADS_TO，并把元素图像向量写入 Pinecone。
6. `process_and_update_chain` 读取页面-元素-页面三元组，生成增强描述并写回 Neo4j。
7. `evolve_chain_to_action` 评估链是否可模板化，生成高阶 Action 节点。
8. `deployment.run_task` 查询高阶动作，尝试匹配当前屏幕元素并执行；失败时回退到 ReAct 模式。

## 8. 屏幕工具与后端服务

### 8.1 解决的问题

`AppAgentX/tool/screen_content.py` 封装了真实设备交互，`AppAgentX/backend/` 提供图像解析和特征提取服务。二者共同解决 GUI Agent 对页面状态的感知和动作执行问题。

### 8.2 数据来源 / 输入格式

屏幕工具输入包括 ADB 设备 ID、截图路径、动作类型、坐标、文本和滑动方向。OmniParser 服务 `POST /process_image/` 接收截图文件，返回 `parsed_content`、`labeled_image` 和耗时。特征服务需要先通过 `/set_model` 设置模型，再调用 `/extract_single/` 或 `/extract_batch/` 提取特征。

### 8.3 训练方式 / 推理方式

后端服务使用已有模型推理，不在 AppAgentX 主流程中训练。OmniParser 依赖 `weights/icon_detect_v1_5/best.pt` 和 `weights/icon_caption_florence/`。ImageEmbedding 使用 `timm` 加载特征模型，默认由调用方请求 `resnet50`。

### 8.4 评测方式

复现阶段需要验证两个服务端口：OmniParser 在 `8000`，ImageEmbedding 在 `8001`。可分别检查 `/process_image/` 是否返回元素 JSON，`/model_info` 或 `/extract_single/` 是否正常返回特征维度和耗时。还需验证 Docker GPU 支持和模型权重是否放在 README 指定位置。

### 8.5 对当前方案的意义

这部分是复现的外部依赖核心。没有 OmniParser，智能体无法得到页面元素；没有 ImageEmbedding，元素向量入库和视觉匹配会失败。复现时应先启动后端，再启动 Gradio。

## 9. 链理解模块

### 9.1 解决的问题

`AppAgentX/chain_understand.py` 解决原始操作链缺少语义解释的问题。它从 Neo4j 查询三元组链，对每个三元组生成操作上下文、用户意图、状态变化、任务关系和增强页面/元素描述，并写回对应 Page 和 Element 节点。

### 9.2 数据来源 / 输入格式

输入是 Neo4j 中某个起始 Page 的 `page_id`。链结构由 `get_chain_from_start` 返回，每个三元组包含 `source_page`、`element`、`target_page` 和 `action`。如果页面节点包含 `raw_page_url`，模块会读取源页面和目标页面图片并转成 base64 传给 LLM。

### 9.3 训练方式 / 推理方式

该模块使用 LangChain LCEL 和 `ChatOpenAI` 推理，不训练模型。输出由 `JsonOutputParser` 约束为 `TripletReasoning` 字段。

### 9.4 评测方式

可评测三元组处理成功率、JSON 解析失败率、写回 Neo4j 成功率、增强描述覆盖率。后续实验可人工抽样检查描述是否忠实于页面和动作，或比较增强描述前后的高阶动作生成成功率。

### 9.5 对当前方案的意义

链理解是从记录数据到可复用技能之间的中间层。复现时需要先确保 Neo4j 中有完整链，再调用该模块，否则会返回空列表。

## 10. 链进化模块

### 10.1 解决的问题

`AppAgentX/chain_evolve.py` 解决如何把低级操作链转为高阶动作的问题。它先评估链是否具备模板化价值，再生成 Action 节点字段，包括动作名、描述、前置条件、元素序列和模板匹配条件。

### 10.2 数据来源 / 输入格式

输入是起始页面 `page_id`。模块从 Neo4j 中读取完整链，并将任务描述、链操作、元素细节和链理解结果格式化后传给 LLM。

### 10.3 训练方式 / 推理方式

该模块使用 LLM 推理，不训练模型。`evaluate_chain_templateability` 输出是否可模板化及置信度，`generate_action_node` 输出高阶动作结构，`create_action_node_in_db` 和 `create_action_element_relations` 负责写入 Neo4j。

### 10.4 评测方式

可记录模板化通过率、Action 节点创建成功率、COMPOSED_OF 关系完整率、生成字段完整率。后续可评测同类任务复用成功率、平均步骤减少比例、错误执行率和人工审核通过率。

### 10.5 对当前方案的意义

这是 AppAgentX 的关键创新点在代码中的实现位置。复现时只要能从一条人工或自动轨迹生成 Action 节点，就说明记忆到高阶动作的主链路已打通。

## 11. 部署执行模块

### 11.1 解决的问题

`AppAgentX/deployment.py` 解决高阶动作如何用于新任务执行的问题。它尝试将用户任务匹配到已有高阶动作，解析当前屏幕，匹配模板元素与当前元素，执行动作序列；如果无法匹配或执行失败，则回退到 ReAct 模式。

### 11.2 数据来源 / 输入格式

输入是用户任务描述和 ADB 设备 ID。运行时会读取 Neo4j 中的 Action、Element、Shortcut 相关信息，并读取当前屏幕的 OmniParser 解析结果。

### 11.3 训练方式 / 推理方式

该模块不训练模型。任务到高阶动作匹配、语义元素匹配、shortcut 条件判断和模板生成使用 LLM；视觉匹配依赖元素特征向量或实时特征提取；动作执行依赖 ADB。

### 11.4 评测方式

可评测高阶动作命中率、模板执行成功率、单步元素匹配准确率、回退到 ReAct 的比例、回退后任务成功率、部署执行平均步骤数和平均耗时。

### 11.5 对当前方案的意义

该模块是检验链进化是否有实际价值的地方。复现时需要注意当前代码存在字段命名不完全一致的风险：链进化创建的是 `element_sequence`，部署路径部分逻辑读取 `action_sequence`。这不会影响文档创建，但后续复现执行时需要重点验证并修正。

## 12. 配置、依赖与安全边界

### 12.1 关键配置

`AppAgentX/config.py` 包含 LLM、LangChain、Neo4j、OmniParser、ImageEmbedding 和 Pinecone 配置。当前文件中存在占位 API key 和默认本地端口。复现时应使用本地配置或环境变量管理真实密钥，不应把真实密钥提交到仓库。

### 12.2 运行依赖

`AppAgentX/requirements.txt` 包含 Gradio、Neo4j、LangChain、LangGraph、OpenAI SDK、Transformers、Torch、Pillow、OpenCV 等依赖。后端服务另有各自 requirements。项目还依赖 Android ADB、Docker、Docker Compose、NVIDIA GPU 支持和 OmniParser 权重。

### 12.3 数据与产物

运行产物包括截图、标注图、元素 JSON、状态 JSON、Neo4j 数据和 Pinecone 向量。当前仓库没有确认内置 benchmark 数据集。若后续引入任务集，应单独记录数据来源、许可、是否受 NDA 限制和本地路径配置。

## 13. 复现建议流程

1. 创建并激活仓库根目录 `.venv/`。
2. 安装 `AppAgentX/requirements.txt` 和后端服务依赖。
3. 准备 OmniParser 权重：`OmniParser/weights/icon_detect_v1_5/best.pt` 和 `OmniParser/weights/icon_caption_florence/`。
4. 在 `AppAgentX/backend/` 下启动 Docker Compose，确认 `8000` 和 `8001` 服务可用。
5. 配置 `AppAgentX/config.py` 中的 LLM、Neo4j、Pinecone、OmniParser 和 Feature URI。
6. 启动 Neo4j，确认连接地址和账号密码可用。
7. 连接 Android 设备或模拟器，确认 `adb devices` 能列出设备。
8. 在 `AppAgentX/` 下启动 `python demo.py`。
9. 在 Gradio 中初始化设备和任务。
10. 使用人工探索或自动探索生成短轨迹，并保存为 JSON。
11. 在 “Chain Understanding & Evolution” 中刷新 JSON、写入数据库、理解操作链、生成高阶动作。
12. 在 “Action Execution” 中输入相似任务，测试高阶动作是否可复用；失败时观察 ReAct 回退日志。

## 14. 验证方法与预期输出

### 14.1 文档验证

命令：

```bash
test -f memory-bank/architecture.md && sed -n '1,80p' memory-bank/architecture.md
```

预期输出：能够看到本文档标题 `# AppAgentX 架构说明` 和 `## 1. 方案概述`。

### 14.2 工作区验证

命令：

```bash
git status --short
```

预期输出：至少包含新增文件 `memory-bank/architecture.md`，不应出现 AppAgentX 代码文件被修改。

### 14.3 后端服务验证

命令：

```bash
cd AppAgentX/backend && docker-compose ps
```

预期输出：`image-embedding` 和 `omni-parser` 两个服务处于运行状态。若权重缺失，容器可能能启动但 `/process_image/` 调用会失败。

### 14.4 ADB 验证

命令：

```bash
adb devices
```

预期输出：至少有一个设备或模拟器 ID，状态为 `device`。

### 14.5 Gradio 验证

命令：

```bash
cd AppAgentX && python demo.py
```

预期输出：Gradio 服务启动，并在页面中能刷新 ADB 设备列表。若 LLM、Neo4j、Pinecone 或后端服务未配置，后续按钮调用会在对应步骤报错。

## 15. 当前无法仅根据仓库确认的内容

- 原论文实验中使用的完整 benchmark 任务集、任务数量和具体指标，需要结合论文或原始实验配置进一步确认。
- 本仓库当前没有提供可直接运行的示例状态 JSON 或 Neo4j dump，因此数据库内容需要通过实际探索流程生成。
- `Shortcut` 节点的创建路径在当前代码中未找到，仅看到部署阶段的读取逻辑；该部分需要根据原项目后续代码或运行数据进一步确认。
- AppAgentX 的正式实验结果不能从当前仓库代码推断，本文档不记录未验证数值。

## 16. 后续改造重点

1. 统一轨迹 JSON、Neo4j Action 节点和部署执行之间的字段命名，尤其是 `element_sequence` 与 `action_sequence`。
2. 为 Neo4j 增加唯一约束和索引，避免多次复现实验写入重复节点后难以定位。
3. 增加一条最小可复现脚本：检查 ADB、后端服务、Neo4j、Pinecone、LLM 配置，并输出明确失败原因。
4. 将真实 API key 从 `config.py` 移出，改为本地未提交配置或环境变量。
5. 给自动探索加入最大步数、超时、失败分类和结构化日志，方便做可重复实验。
6. 给链进化结果加入人工审核或离线评测，避免低质量高阶动作进入部署执行。

## 17. 第 1 步环境准备后的文件作用补充

- `.venv/`：仓库根目录虚拟环境，承载 AppAgentX 主依赖；该目录为本地运行产物，不提交。
- `AppAgentX/requirements.txt`：主应用依赖入口，覆盖 Gradio、LangChain、LangGraph、Neo4j、Torch、Pillow 等运行依赖。
- `AppAgentX/config.py`：配置模块；第 1 步只验证可导入，不写入 Key，也不连接外部服务。
- `AppAgentX/data/State.py`：状态结构模块；第 1 步通过导入验证其语法和基础依赖可用。
- `AppAgentX/tool/screen_content.py`：ADB 与屏幕工具模块；第 1 步只验证可导入，实际设备操作留到第 5 步。
- `AppAgentX/backend/`：后端服务目录；第 1 步只确认目录和 Docker 环境，容器启动与服务接口验证留到第 4 步。
- `memory-bank/plan.md`：复现步骤清单；当前已有第 1 至第 6 步的任务边界。
- `memory-bank/results.md`：实验结果记录文件；第 1 步完成后记录环境验证结果。
- `memory-bank/progress.md`：复现过程记录文件，用于给后续开发者说明已执行动作、验证结论和剩余阻塞项。

## 18. 第 2 步凭据准备后的文件作用补充

- `/home/tiger/.config/appagentx/credentials.env`：仓库外本地凭据文件，保存 LLM、Neo4j、Pinecone 的连接字段；不提交，不在文档中记录真实值。
- `scripts/verify-step2-credentials.sh`：第 2 步验证脚本，只检查凭据文件路径、权限、字段完整性、基础格式和仓库外位置，不打印 Key、密码或完整 URI。
- `AppAgentX/config.py`：仍未在第 2 步修改；第 3 步才会把已验证的本地凭据信息同步到运行配置。
- `memory-bank/progress.md`：记录第 2 步已完成的验证结论，方便后续开发者知道凭据已准备但尚未写入 `config.py`。
- `memory-bank/results.md`：记录第 2 步凭据准备结果，只保留验证状态，不记录敏感内容。

## 19. 第 3 步配置后的架构补充

- `AppAgentX/config.py`：配置入口已改为优先加载仓库外 `credentials.env`，再暴露原有字段名；调用方仍通过 `config.LLM_BASE_URL`、`config.Neo4j_URI`、`config.PINECONE_API_KEY` 等读取配置。
- `/home/tiger/.config/appagentx/credentials.env`：本地真实配置来源；Neo4j Aura 需要使用 `neo4j+s://` 安全 URI 才能通过 driver 路由验证。
- `AppAgentX/requirements.txt`：已补充 `pinecone`，与 `AppAgentX/data/vector_db.py` 中 `from pinecone import Pinecone, ServerlessSpec` 对齐。
- `scripts/verify-step3-config.py`：第 3 步连通性验证脚本，按 LLM、Neo4j、Pinecone 分项检查并汇总失败；LLM 检查忽略环境代理，避免本地坏代理影响验证。
- `AppAgentX/data/vector_db.py`：Pinecone 索引默认仍为 `area-embedding`，维度 `2048`，serverless 区域 `aws/us-east-1`。
- `AppAgentX/data/graph_db.py`：Neo4j driver 使用 `config.Neo4j_URI` 和 `config.Neo4j_AUTH`，第 3 步只验证连接，不创建节点或写入数据。

## 20. 第 4 步 backend 本地替代后的架构补充

- `AppAgentX/backend/docker-compose.yml`：原计划入口，用于启动 `image-embedding` 和 `omni-parser`；当前容器环境缺少 Docker build/pull 所需权限，因此第 4 步未采用 Docker 路线。
- `AppAgentX/backend/ImageEmbedding/image_embedding.py`：ImageEmbedding FastAPI 服务入口；本地监听 `8001`，验证接口包括模型列表、模型设置、模型信息和单图特征提取，输出特征维度为 `2048`。
- `AppAgentX/backend/OmniParser/omni.py`：OmniParser FastAPI 服务入口；本地监听 `8000`，`POST /process_image/` 接收截图，调用 YOLO、OCR 和 Florence caption，返回元素 JSON、标注图和耗时。
- `AppAgentX/backend/OmniParser/utils.py`：OmniParser 核心工具；第 4 步增加本地运行兼容逻辑，包括 OCR lazy 初始化、PaddleOCR 3.x 参数适配、PaddleOCR 失败降级为空 OCR、空 OCR 框结构统一。
- `AppAgentX/backend/OmniParser/flash_attn/__init__.py`：本地占位模块，用于通过 Florence-2 动态代码的静态导入检查；由于没有真实包元数据，Transformers 仍不会启用 `flash_attn` 分支。
- `AppAgentX/backend/OmniParser/requirements.txt`：OmniParser 后端依赖入口；第 4 步固定 Florence/Transformers 兼容版本，避免过新 Transformers 要求更高 PyTorch 版本。
- `AppAgentX/backend/OmniParser/weights/`：OmniParser 本地权重目录；关键文件包括 `icon_detect_v1_5/best.pt` 和 `icon_caption_florence/model.safetensors`，该目录属于运行依赖和大文件产物，不应提交权重。
- `scripts/verify-step4-backend.py`：第 4 步 backend 验证脚本；支持 Docker 服务为空时进入本地模式，检查 `8001`、`8000`、ImageEmbedding 特征提取和 OmniParser 图片解析。
- `/tmp/appagentx-image-embedding.log`、`/tmp/appagentx-omni-parser.log`：本地 uvicorn 日志文件，用于排查启动和接口请求错误，不属于仓库产物。

## 21. 第 5 步 ADB 与模拟器后的架构补充

- `/home/tiger/android-sdk/`：本地 Android SDK 安装目录，提供 `platform-tools/adb`、`emulator/emulator`、`cmdline-tools/latest/bin/sdkmanager` 和 `avdmanager`；该目录在仓库外，不提交。
- `appagentx_api36`：第 5 步创建的 Android 36 AVD；当前环境没有 `/dev/kvm`，需要用 `emulator -avd appagentx_api36 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect -accel off` 启动。
- `emulator-5554`：第 5 步验证通过的 ADB 设备 ID；后续 Demo 或探索流程应使用 `adb devices` 的实际在线设备 ID，不假设该 ID 永远不变。
- `scripts/verify-step5-adb.py`：第 5 步设备验证脚本；优先把 Android SDK 的 `platform-tools` 加入 `PATH`，再检查 ADB、设备状态、屏幕尺寸和项目截图工具。
- `AppAgentX/tool/screen_content.py`：屏幕工具模块；`get_device_size` 已通过项目工具验证可读取 `1080x1920`，`take_screenshot` 已支持 `/sdcard` 失败后回退到 `/data/local/tmp`。
- `log/step5_screenshots/`：第 5 步截图验证输出目录，属于运行产物；用于确认项目截图工具能从设备拉取 PNG，不应作为正式数据集提交。

## 22. 第 6 步 Demo 验证后的架构补充

- `AppAgentX/demo.py`：Gradio Demo 主入口；第 6 步验证了 `Initialization` 和 `User Exploration` 两个页签的最小链路。`start_session` / `stop_session` 已修正为与 9 个 Gradio outputs 对齐。
- `AppAgentX/explor_human.py`：人工探索执行模块；`capture_and_parse_page` 能调用截图工具和 OmniParser，`single_human_explor` 能把人工动作写入 `history_steps`。
- `AppAgentX/log/screenshots/`：Demo 人工探索截图、标注图和解析 JSON 的运行目录；用于页面可视化和后续状态 JSON 引用，不属于源码。
- `AppAgentX/log/json_state/`：`Stop Session` 后的状态 JSON 输出目录；第 6 步最小验证以这里生成的新 JSON 作为轨迹采集成功标志。
- `AppAgentX/data/data_storage.py`：状态导出模块；本步骤只使用 `state2json` 生成文件，未调用 `json2db` 入库。
- `AppAgentX/backend/OmniParser/`：Demo 人工探索依赖 `8000/process_image/` 生成元素标注图和 JSON；backend 服务掉线会直接导致 `Start Session` 无法完成解析。
- `AppAgentX/backend/ImageEmbedding/`：第 6 步前置健康检查仍验证 `8001`，但本步骤人工探索未执行入库和向量写入，因此不直接调用特征提取。
- VS Code 端口转发 `7860`：用于在本地浏览器访问远程 Gradio Demo；这是运行环境配置，不是仓库文件。
