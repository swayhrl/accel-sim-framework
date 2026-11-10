# AI-ARCH｜Hybrid/GDN/KV 真实执行资格调查 V1

日期：2026-11-10。执行端：109-AI-ARCH API。范围：固定资料、109 指定路径和已安装源码的只读 CPU 核查；没有加载模型、初始化 CUDA、获取 GPU 锁或下载权重/数据。

## 裁决

**`NO_GPU_PROBE_READY / QUALIFICATION_STOP`。** Qwen3.5-4B 是有明确官方配置、可定义纯文本混合状态合同的候选模型；109 已安装的 vLLM 也有 Qwen3.5/GDN 静态入口。但在本轮检查的本地模型根和缓存中没有该模型的完整权重，也没有可固定字节与使用权的自然多轮会话内容。运行时的 SM89 实际后端、状态恢复正确性、完整请求质量和同活容量均未执行验收。因此现在不能写 GPU 探针合同，更不能以 A70N 的源码审阅或新论文作者数字代替本机准入。

这是**本轮已检查范围内的资格未通过**，不是 Hybrid/GDN/KV 的性能负结果，也不证明节点上所有未检查目录均无资产。A70N 原结论 `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE / NO_SURVIVOR_IN_SEARCH_SCOPE` 维持；本轮新增的是资产与本机运行时身份核查，并未重跑 A70N 源码审计。

## 固定来源与对象

| 层次 | 固定身份与证据作用 |
| --- | --- |
| 项目旧审查 | A70N 执行 `5076223db5db0256fd0ccacec50b5347a0cab8c5`、A71 独审 `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE`；[A70N 原报告](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md)。 |
| 本轮论文判断 | [2026-11-10 文献报告](https://github.com/swayhrl/accel-sim-framework/blob/4642b573f0b5aa3faa3cf2fa705bed3b66ee109a/docs/ai_workload_research/reviews/AI_ARCH_LITERATURE_AND_NEXT_DIRECTION_20261110/AI_ARCH_LITERATURE_AND_NEXT_DIRECTION_20261110.md)：SARIA、Storage View、FlashOffloading、SPARE、低位 GDN 和状态转接均是直接近邻，但不提供本机资产或质量资格。 |
| 模型 | A70N 固定 `Qwen/Qwen3.5-4B@851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` 的 config 与 Apache-2.0 元数据，32 层中 24 GDN＋8 full attention；本轮未重新取得 Hugging Face 元数据，公开 API 连接在 TLS 握手时被重置。模型仍是**历史已核来源**，不是本轮已核本机权重。 |
| 109 软件 | `/data/c16/envs/c16-vllm-v0.30.0-sm89-v1` 中 `vllm-0.30.0`、`transformers-5.18.0`；vLLM registry 有 `Qwen3_5ForCausalLM` 和 `Qwen3_5ForConditionalGeneration`，model 文件调用 `QwenGatedDeltaNetAttention`。只证明静态源码入口，不证明该官方 checkpoint 可在 109 加载、数值通过或服务可用。 |

## 准入门逐项核查

| 门 | 需要的可复核证据 | 本轮所见 | 结果 |
| --- | --- | --- | --- |
| G1 真实模型 | 官方 revision、许可、完整权重/索引/tokenizer 的字节身份及本机可读位置，明确选完整多模态 checkpoint 的纯文本路径还是官方 text-only checkpoint。 | A70N 有官方 config/revision；只读检索 `/data/c16/models`、`/data/c16/cache` 和 `/home/huangrulin/.cache/huggingface/hub` 中相应浅层目录，未发现 `Qwen3.5`。没有读取/下载权重，也没有把其他 Qwen 资产冒充 3.5。 | **未通过**：本轮无可执行本机模型身份。 |
| G2 自然会话 | 合法来源、完整多轮 prompt 内容或 token ID、session/turn/完成标记、版本与 hash，探索和独立验证分离。 | 已知 A70M 资产目录是文献/源码整理；109 的 Hugging Face datasets cache 不存在。本轮限定路径下没有合格会话内容。SARIA 的 TraceLab/WEKA 仅记录长度与块身份，作者重建合成 prompt。另一篇 [Storage View, 2611.10178v1](https://arxiv.org/abs/2611.10178v1) §3.3/附录表 1 指出 WildChat 和 Exgentic 含原始文本与会话结构，可作为**待核的公开输入候选**，但本轮未取得数据、许可或字节身份。 | **未通过**：不可用合成前缀冒充自然会话；公开候选不等于本机准入。 |
| G3 同语义强运行时 | 同一模型/精度/TP、GDN 状态与 KV 的端点恢复、prefix 命中和复制语义；确认 SM89 上实际 kernel/config、兼容的强对照及版本。 | vLLM 0.30.0 包含 Qwen3.5/GDN 源码。安装版 `qwen_gdn_linear_attn.py` 的 `_resolve_gdn_prefill_backend` 仅将 SM90、合格 SM100/120 选入 FlashInfer，SM89 会走 `Triton/FLA`；FLA 在 vLLM 包内。此 venv 未见 SGLang；A70N 所述 ReplaySSM fork 不能等同本机默认路径。没有运行模型、选后端、检测 ABI/数值。 | **静态部分成立，执行资格未知**。不得称 FlashInfer 强路径已在 4080 启用。 |
| G4 数值、质量与容量 | 固定 tokenizer/状态精度/请求集合，对完整请求与 checkpoint 恢复做同模型质量及逐步状态核对；记录模型、KV、GDN、图/临时态同活峰与容量门。 | A70N 的纯内容算术独立复算：24 层一套 GDN＋conv 状态 `51,511,296 B = 49.125 MiB/序列`，8 full 层 BF16 KV `32,768 B/token`，内容交点 1,572 token。此数不含权重、padding、别名并集、scratch、graph 或并发峰。本轮没有可测模型和会话。 | **未知**：不能凭 16 GiB 标称容量或内容算术登记 PASS。 |

资产检查是明确路径的浅层名称核对，不遍历 `/data/c16` 其它项目资产，也不访问 164/挂载。`EVIDENCE.json` 登记路径、源码 SHA-256、检查结果和证据边界。

## 与新论文的差异和研究价值

SARIA 的真实模型执行主要发生在 96 GiB RTX PRO 6000；其 trace 没有 prompt 内容，请求终止于首 token；A30 辅台用随机初始化缩小结构。Storage View 的 TTL 提升来自 trace 驱动策略账，不是具体容量系统的完整请求加速。SPARE 与低位 GDN 改变状态表示或精度并触发质量门；跨模型状态转接改变模型身份。它们使“多放一层 KV/GDN cache”缺乏独特性，却没有回答：**在同一真实模型、原精度、自然多轮内容和兼容强 runtime 下，状态生命周期是否还有暴露在完整请求关键路径上的物理服务量？** 这个问题值得资格调查，但当前证据还不足以升级为 GPU 实验。

## 最小后续合同与停止条件

1. **资产身份先行。** 仅在将来有明确模型/数据获取或已有资产位置后，固定官方 checkpoint 与 tokenizer 的 revision/文件 hash/许可；优先核 WildChat 的自然多轮文本或 Exgentic 的自然 agent 轨迹，逐一确认内容、会话完成信号、使用权和独立验证集合。WildChat 没有天然任务质量 gold；Exgentic 的固定轨迹回放不能冒充 Qwen3.5 自由生成的 agent 成功率。若仍只有 config、trace 长度或合成 prompt，维持 `NO_GPU_PROBE_READY`。
2. **纯 CPU 合同冻结。** 从固定 config 推导 FA/GDN/conv 状态形状、dtype、版本与重用端点；选一条实际兼容 SM89 的 vLLM 强路径，记录 MTP/量化/压缩关闭情况及允许的参考质量判据。不能拼接 vLLM、SGLang 和 ReplaySSM 互斥特性为虚构基线。
3. **只有另立获准 GPU Goal 才做原生准入。** 在共享资源准入和当前窗口下，先验证模型加载、完整请求、prefix/checkpoint 正确性与同活容量；再考虑 baseline/诊断/独立会话三组最小比较。完整 arrival→首 token/结束、输出质量、Host 与 GPU 各自时钟、state/KV 物理并集和关键路径分账。若加载/数值/质量/容量失败，或强软件后差值未超过噪声，立即 STOP；局部 kernel 或逻辑字节变化不晋升硬件候选。

本轮已完成所授权的 CPU 资格调查，结论为 **无 GPU 探针资格，STOP**。没有申请或占用 GPU，也没有改变协调分支、A70N 旧裁决或其它项目状态。
