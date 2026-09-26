# Round07｜Post-R53长时无人值守候选：R54 exact recurrent-state checkpoint lifecycle

日期：2026-09-27。维护：ChatGPT。**文献/源码与实验设计；本文件本身不启动109/174。**

## 1. R53冻结

Accepted R53 execution:
- branch `hrl/awma-r53-online-legal-workset-native-qualification-v1`
- commit `843ad43ad33153bf73a0e51aed6d8ac309356cae`
- final `R53_ALGORITHM_CHANGE_NOT_MAPPING_GAIN_V1`

独立审查确认：
- A1_PACKED在GSM8K/HumanEval分别减少约12.3%/21.6% token rows，但trajectory和final tokens均改变；
- A1_SAFE_BUCKET精确恢复trajectory/final tokens，但forward/token-row work回到A0；
- 所以当前Fast-dLLM-v2部署中没有被证明的semantically legal mapping reduction。
R53停止，不通过放松语义合同继续找正例。

## 2. 为什么下一步优先R54，不优先R55

### R54近邻

- Marconi (MLSys 2025): hybrid/SSM prefix cache的admission/eviction和state/KV联合管理；核心是缓存实用性，不是逐次snapshot production cost。
- Sparse Prefix Caching (2605.05219): exact recurrent-state checkpoints稀疏放置，命中后从最深checkpoint恢复并exact重算suffix；核心是checkpoint placement/Pareto，不要求新recurrent kernel。
- Tail-Replay (2608.30310): 不保存recurrent checkpoint，以短tail replay近似重建linear-attention state；这是approximate方案。
- TreeWY (2608.20961): Gated DeltaNet speculative verification，避免每个draft位置保存recurrent-state snapshot；针对speculative tree。
- Persistent-State Dataflow Accelerator (2603.05931): 指出GDN decode主动recurrent state每token HBM round-trip是memory-bound，并用FPGA片上持久state处理；这是active-state decode，不是prefix checkpoint materialization。
- DAMP (2608.27513): recurrent-state mixed-precision quantization，针对active state的容量/带宽。

这些工作说明“recurrent state大/贵”不是新发现。仍可核查的窄问题是：

> 对exact prefix checkpoint，状态本来就必须可恢复；在强软件预分配和异步/层级交叠copy之后，checkpoint **生产与恢复本身**是否仍成为有材料性的生命周期成本？

这不是checkpoint placement、approximate replay、active-state quantization或speculative state elimination的简单重复。

### R55近邻/平台边界

- NVIDIA Transformer Engine NVFP4显式需要rowwise和columnwise quantized tensors，列向数据/scale以转置布局保存。
- Stable FP4 Training via Transposition-Invariant Block Quantization (2607.24953)直接从1D block transpose scale inconsistency出发提出2D block FP4。
- NVIDIA NVFP4 pretraining和Quartet II已经覆盖稳定训练/梯度量化，MOSS覆盖online scaling/dequantization overhead。

RTX4080不是NVFP4原生训练平台。在本节点做软件仿真无法支持真实低比特硬件吞吐/数据移动结论。
因此R55本轮只做source/closest-work更新，不做Native性能实验，不作为十小时任务主线。

## 3. R54真实模型候选

唯一候选：
`Qwen/Qwen3.5-0.8B`

建议固定HF revision：
`c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`

公开模型卡记录：
- 0.8B；
- hidden 1024；
- 24 layers；
- 6 × [3 × (Gated DeltaNet→FFN) + 1 × (Gated Attention→FFN)]；
- 即18个GDN层+6个full-attention层；
- GDN 16 QK/16 V heads, head dim 128。

权重约1.75GB，适合109/4080资格实验。

这不是所有hybrid/recurrent模型的代表；结果仅限Qwen3.5-0.8B的GDN hybrid。

## 4. R54科学问题

`R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1`

对固定prefix和exact model semantics：

1. exact recurrent-state checkpoint有多少bytes，哪些tensor必须随checkpoint保存？
2. naïve exact snapshot的blocking成本是多少？
3. 预分配+source-correct异步/layer-staggered snapshot后，生产成本是否仍material？
4. exact restore+suffix replay是否逐bit/greedy语义闭合？
5. restore成本相对full-prefix recompute、相对checkpoint所节省的计算是否material？
6. 在有限共享-prefix复用次数下，包含checkpoint production+restore后的break-even reuse count是多少？

只有5%级以上且稳定、且不能由host/Python或明显低效copy解释的剩余成本，才进入架构审查。

## 5. 实验结构

### Source/runtime audit

先验证Transformers/Qwen3.5 cache object中：
- full-attention KV；
- GDN conv state；
- GDN recurrent state；
- initialization flags/metadata；
哪些构成exact restore authority。

需要从真实runtime对象枚举，而不是按论文公式猜bytes。

必须使用fast GDN path；若节点只能落到明显慢的PyTorch reference，在两次bounded工程修复后仍不能获得可信fast path，则本方向Native不合格。

### Prefix input

不再下载新benchmark数据集。复用已经冻结的R53 GSM8K/HumanEval raw prompts，按固定顺序拼接并tokenize，形成一个内容真实但用途明确的shared-prefix fixture。

预注册prefix lengths:
- 2048
- 4096

不足时按冻结request顺序循环拼接，并在manifest记录。
这是prefix-cache micro-workload，不冒充线上命中分布。

### Arms

P0 `NO_CHECKPOINT`: 相同chunked prefill，无snapshot。

P1 `SYNC_PREALLOC_CHECKPOINT`: 预分配destination，边界处完整exact D2D copy；不做allocator/clone混杂。

P2 `ASYNC_STAGGERED_CHECKPOINT`: 强软件baseline。按source-correct layer/state readiness，预分配并用events/side stream尽量与后续可独立工作交叠；不得在source即将原地更新时产生race。若layer-stagger不能合法实现，需说明依赖边界，不能伪造overlap。

Checkpoint densities固定两个：
- every 512 tokens
- every 2048 tokens
不扫更多点。

### Restore

固定从一个合法checkpoint恢复，继续到4096 boundary，然后执行一个greedy decode token。

比较：
- uninterrupted reference；
- restore+suffix。

必须闭合：
- cache/state structure；
- greedy next token；
- required recurrent/conv/KV state hashes where exact comparison is meaningful；
- final logits/hidden numerical boundary。

若不能证明restore语义，不能做性能结论。

### Reuse/amortization

使用测得成本计算而非重新跑服务系统：
- 1、2、4个suffix reuse scenarios；
- total = one prefix materialization + checkpoint production + N×restore/suffix；
- 对照N×full prefix recompute。

这是amortization model，必须标明测量项和推导项。

## 6. 停止/推进

- snapshot/restore runtime identity无法闭合 → INPUT_OR_RUNTIME_NOT_QUALIFIED
- exact restore语义失败 → RESTORE_SEMANTICS_NOT_QUALIFIED
- 强软件snapshot production overhead <5% prefill且restore成本低于5% saved recompute → SOFTWARE_LIFECYCLE_COST_LOW
- 成本主要是host/Python/allocator且可通过预分配/异步关闭 → SOFTWARE_BASELINE_SUFFICIENT
- 强软件之后仍有>=5%稳定GPU-local snapshot/restore成本，并且closest-work不直接覆盖 → RESIDUAL_READY_FOR_ARCH_REVIEW

不因snapshot bytes大就直接授权机制。

## 7. 十小时无人值守策略

主线R54从source audit→模型/runtime→canary→snapshot correctness→strong baseline→formal timing→restore→amortization→closest-work check→final closure，一轮到底。

并行CPU支线：
- 更新R55 source/closest-work map；
- 不运行R55 GPU benchmark；
- 若R54在runtime/source gate早停，用剩余时间做R54/R55/最新hybrid-state related-work补全，但不自动跳入第三个GPU问题。

不启动174，除非R54最终达到READY_FOR_ARCH_REVIEW；即便达到，也只生成下一阶段174 manifest，不执行。

## 8. 来源

- Marconi: https://arxiv.org/abs/2411.19379
- Sparse Prefix Caching: https://arxiv.org/abs/2605.05219
- Tail-Replay: https://arxiv.org/abs/2608.30310
- TreeWY: https://arxiv.org/abs/2608.20961
- Persistent-State Dataflow Accelerator: https://arxiv.org/abs/2603.05931
- DAMP: https://arxiv.org/abs/2608.27513
- Qwen3.5-0.8B: https://huggingface.co/Qwen/Qwen3.5-0.8B
- Transformer Engine NVFP4: https://nvidia.github.io/TransformerEngine/features/low_precision_training/nvfp4/nvfp4.html
- Stable FP4 Transposition-Invariant BQ: https://arxiv.org/abs/2607.24953
- Quartet II: https://arxiv.org/abs/2601.22813
- MOSS: https://arxiv.org/abs/2511.05811
