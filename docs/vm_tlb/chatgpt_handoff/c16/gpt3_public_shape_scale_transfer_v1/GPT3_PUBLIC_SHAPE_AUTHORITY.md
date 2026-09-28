# GPT-3 Public-Shape Authority for C16 Scale-Transfer V1

本文件只冻结本实验所需的公开结构事实与证据边界，不提供原始GPT-3权重。

来源阅读记录：
- C16 LR08 commit：`139135231fb30b4981eedb031da9c7e182269652`
- LR08 path：`docs/vm_tlb/literature_notes/c16/rounds/2026-09-28_LR08_GPT3_WORKLOAD_ACCESS_AND_SINGLE_GPU_FEASIBILITY.md`
- OpenAI GPT-3论文：Brown et al., arXiv:2005.14165，Table 2.1 / §2.1
- OpenAI官方`openai/gpt-3`仓库未提供原始训练权重下载；因此本实验不得声称原始checkpoint执行。

GPT-3-175B公开结构：
- layers = 96
- hidden H = 12288
- attention heads = 96
- head dimension = 128
- FFN intermediate = 4H = 49152
- original context window = 2048
- FFN是两层GELU式Dense FFN，不是Qwen gate/up/down三投影
- 原论文attention包含dense/local-banded-sparse交替；本任务只研究FFN公开尺寸，不重建attention。

本实验只使用FFN两个主矩阵：
- expand：K=12288, N=49152
- contract：K=49152, N=12288

证据分类：
- FP16 Dense：GPT-3公开尺寸的合成shape anchor
- W4：GPT-3公开尺寸映射到既有AutoAWQ kernel的机制代理

两者都不是原始GPT-3权重、自然激活或完整模型性能。
