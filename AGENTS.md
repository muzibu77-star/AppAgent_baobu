# Agent 工作指南

本文件为 Codex 在此代码库中工作时提供指导。

---

## 一、开发前必读

每次写任何代码前，必须完整阅读 `memory-bank/architecture.md`（包含完整数据库结构与模块设计）。
每完成一个重大功能或里程碑后，必须同步更新 `memory-bank/architecture.md`。

---

## 二、虚拟环境要求

- 本项目统一使用仓库根目录下的 `.venv/` 作为 Python 虚拟环境。
- 后续新建或重建虚拟环境时，仍使用 `.venv/`，不得直接使用全局 Python 环境安装项目依赖。
- `.venv/` 已由 `.gitignore` 忽略，不提交到仓库。
- 运行任何 Python 脚本、数据检查、训练或评估前，必须先激活虚拟环境。

**创建环境**

优先使用：

```bash
python3 -m venv .venv
```

如果系统缺少 `ensurepip` 或 `python3-venv`，使用：

```bash
python3 -m virtualenv .venv
```

**激活环境**

```bash
source .venv/bin/activate
```

**退出环境**

```bash
deactivate
```

**step1 最小依赖**

```bash
pip install \
  "numpy==1.26.4" \
  "pandas==2.2.2" \
  "pyarrow==14.0.2" \
  "datasets==2.14.5" \
  "fsspec==2023.6.0" \
  "transformers==4.32.0" \
  "peft==0.5.0" \
  "accelerate==0.23.0" \
  "huggingface-hub==0.17.3" \
  "tokenizers==0.13.3" \
  "sentencepiece==0.1.99" \
  "protobuf" \
  "scikit-learn"
```

**验证环境**

```bash
python - <<'PY'
import sys
import torch
import transformers
import peft
import datasets
import accelerate

print("python", sys.version)
print("torch", torch.__version__)
print("transformers", transformers.__version__)
print("peft", peft.__version__)
print("datasets", datasets.__version__)
print("accelerate", accelerate.__version__)
print("cuda_available", torch.cuda.is_available())
print("cuda_device_count", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(f"gpu_{i}", torch.cuda.get_device_name(i))
PY
```

预期输出：
- 命令使用 `.venv/bin/python`。
- 依赖能正常 import 并打印版本。
- CUDA 状态和 GPU 数量有明确输出。

---

## 三、架构与设计原则

- **强制模块化**：必须采用多文件模块化设计，严禁单体巨文件（monolith）。
- **小步迭代**：优先进行小规模、脚本导向的更改，而非大规模框架重构，跑任何训练必须给出进度条、时间累积、剩余时间等便于用户观测任务进度的可视化代码。
- **禁止自主重构**：没有明确指令时，不得重构已有文件结构。只允许定点修改或追加，不得以"更整洁"为由改动未涉及的部分。
- **配置声明式**：配置保持声明式风格，运行任务前须更新所有占位符路径（如 `PATH_TO_VIDEO_CLIPS_OF_SOCCERREPLAY_1988`）。

---

## 四、任务执行规范

**任务拆解**
- 每次对话只处理一个明确的子任务。
- 复杂功能须先拆成任务清单，逐条执行，避免单次改动过多文件。

**执行顺序**
每次给出方案前，必须按以下顺序进行：

1. **声明影响范围**：列出本次改动涉及的文件与函数，经确认后再继续。
2. **说明修改思路**：简要描述实现方案，不要直接给出代码。
3. **列出方案选项**：存在多种实现路径时，列出选项供选择，不擅自决定。
4. **给出验证方法**：完成每个模块后，必须同时提供验证命令与预期输出。

---

## 五、代码风格与命名约定

| 场景 | 规范 |
|------|------|
| 缩进 | 4 个空格（Python） |
| 函数、变量、配置键 | `snake_case` |
| 模型类、数据集类 | `PascalCase` |
| 文件名（通用） | `kebab-case`，如 `user-profile.ts` |
| 文件名（Python 脚本） | 描述性命名，如 `MatchVision_contrastive.py` |
| 导出方式 | 优先使用具名导出（named export），避免默认导出（default export） |

---

## 六、数据与配置安全

- 不得在代码中硬编码私有数据集路径或敏感配置。
- 特定机器的路径存储于本地配置文件，不提交至仓库。
- 不提交大型权重文件。
- 在 PR 描述中注明任何需要保密协议（NDA）的数据集或外部检查点来源。

---

## 七、提交与 PR 规范

**提交信息**
- 使用简短、祈使式的提交摘要。
- 仓库维护类更新可使用中文描述。
- 每次提交应专注且明确指定受影响的模块或区域。

**PR 内容要求**
每个 PR 应包含以下内容：
1. 本次更改的目的与背景。
2. 所需的数据集或检查点路径更新说明。
3. 用于验证的精确命令与预期输出。
4. 若推理行为有变化，附上示例输出或截图。

---

## 八、回答与沟通偏好

- 回复统一使用**中文**。
- 文字类文件（如文档、说明）中不要放置大段代码。
- **严禁无端夸奖**：停止在对话中使用过度礼貌、奉承或"为了夸而夸"的措辞（如：太棒了、你真博学、很有见地等）。
- **平等交流**：保持专业助手与合作伙伴的姿态，语气简洁、真诚且落地，不需要表现出讨好感；如果我的想法有误或可以改进，直接指出，这种专业性比赞美更有价值。
- **禁止使用比喻**：直接给出对应的解释，不使用类比或比喻手法。
