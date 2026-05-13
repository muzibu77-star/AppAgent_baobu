环境激活：cd /home/tiger/BaoBuu/Hungry_Bu/LLaMA_Factory/LLaMA_Factory
source .venv/bin/activate
再运行：llamafactory-cli webui（启动 LLaMA Factory 的图形化网页界面）
退出环境为：deactivate
检查目前卡的空闲状态（nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader）
新建终端实时查看卡的状态：watch -n 1 nvidia-smi（看两个点： Memory是否爆了； GPU-Util是否跑满，正常需要跑满）
执行终端运行 export CUDA_DEVICE_ORDER=PCI_BUS_ID    后，Torch 顺序会和 nvidia-smi 对齐
使用镜像下载，在项目开始前指定：export HF_ENDPOINT=https://hf-mirror.com

本项目本地模型与实验产物目录：
- 根目录 `model/` 只用于存放本地基座模型或模型软链接，不提交到仓库。
- 根目录 `save/` 只用于存放 LoRA adapter、merged 模型、训练日志、评估结果和临时实验产物，不提交到仓库。
- 代码和配置中不得硬编码私有模型路径；本机路径统一放在本地配置文件或环境变量中。
- 默认基座模型使用本地 `Qwen3-4B-Instruct-2507`；若后续显存和时间允许，可把同一流程扩展到更大的 Qwen3 Instruct 模型。
