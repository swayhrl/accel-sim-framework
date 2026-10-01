# LR11：并发强基线、共享缓存上界与下一轮并行机会筛选

日期：2026-10-01。维护者：ChatGPT。状态：文献/源码核查与候选问题设计，不授权GPU或模拟实验。

## 0. 当前项目事实边界

本轮建立在项目已接受事实之上：M1/M1F当前B16 reuse-canary继续timing已因headroom/cost不合算而停止；Qwen2.5-7B AWQ natural FFN已经取得correlation-authoritative timeline；合法FFN wall-clock union约28.48%，显式SiLU+Mul清零whole-decode只约0.22%，而gate/up perfect no-contention concurrency oracle约7.89% decode时间，最小two-stream native baseline已单独冻结并由Lane7执行。

本笔记不把Lane7尚未返回的结果预写成正/负，也不重开M1F、split-K/dequant-cache、旧MoE广播或旧KV展开分支。

## 1. 本轮最重要的新判断

### 1.1 plain gate/up fusion / merge不是新的研究能力

当前vLLM的Qwen2实现直接把HF的`gate_proj`与`up_proj`映射到`gate_up_proj`，使用`MergedColumnParallelLinear`，并把输出交给`SiluAndMul`；同一线性层接口接收`quant_config`。vLLM的模型开发文档也明确把`MergedColumnParallelLinear`定义为weighted-activation FFN常用的多个ColumnParallelLinear合并层，并说明量化方案由linear method注入。当前vLLM AutoAWQ路径在CUDA上还可按硬件/形状选择Marlin类实现。

因此，若C16的two-stream gate/up B1有效，它首先证明“当前AutoAWQ runtime留下了可利用的独立producer并行”，不能直接上升为“gate/up并行是新机制”。更强的软件边界必须至少包含：当前AutoAWQ独立WQLinear_GEMM、two-stream并行、以及语义匹配时的merged gate_up / fused SiluAndMul类实现。真正可能留下研究空间的是：**当merged/fused实现受低比特格式、kernel形状、资源竞争或布局约束限制时，能否在保持各自快kernel的情况下取得接近合并执行的系统收益**。

来源：
- https://docs.vllm.ai/en/v0.12.0/api/vllm/model_executor/models/qwen2/
- https://docs.vllm.ai/en/latest/api/vllm/lora/layers/column_parallel_linear/
- https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/models/qwen2.py
- https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/quantization/auto_awq.py

### 1.2 intra-GPU concurrency已有很强systems近邻；“能并行”本身不新

NanoFlow（OSDI 2025）把compute/memory/network异构操作拆为nano-batch并进行intra-device overlap，同时显式考虑并发干扰；Bullet（ASPLOS 2026）进一步对prefill/decode做动态spatial-temporal sharing；Resonator（ISCA 2026）利用encoder与decoder在SM/HBM上的互补性进行work-conserving co-run。它们共同把“并发执行能提高GPU利用率”变成成熟系统能力边界。

这对当前FFN有两个意义：
1. gate/up是同类W4 GEMM，不具备这些工作最依赖的异构资源互补性，所以two-stream结果若被资源竞争吃掉并不意外；
2. 若未来要做体系结构机制，不能把“额外stream / CTA并发 / 动态资源分配”本身作为创新点，必须找到**现有software co-scheduling在明确资源约束下无法跨越的oracle gap**。

来源：
- NanoFlow: https://www.usenix.org/conference/osdi25/presentation/zhu-kan
- Bullet: https://doi.org/10.1145/3779212.3790135
- Resonator: https://doi.org/10.1109/ISCA66397.2026.00173

### 1.3 PASCAL全文现已可读：它给了我们一个非常适合“oracle-first”的cache gate

LR09/LR10时PASCAL（arXiv:2609.10515）只有摘要可用；本轮已取得arXiv HTML全文。

它研究parallel scan/shared cyclic scan：多个GPU worker扫描同一共享数据但存在progress divergence。关键不是再提出一个replacement policy，而是先给：
- fixed-phase下的closed-form footprint / TTL miss law；
- fully-associative LRU边界；
- **对任意demand-paging replacement policy（包括offline Belady）的policy-independent residency lower bound**；
- 进度差`sigma_E`与保持跨worker sharing所需容量的sharp condition；
- 一个非常重要的反例：**cache traffic可以恶化很多，而时间几乎不变**，因为pipeline overlap/consumer work可以隐藏miss↔hit差异。

这与C16近期多次负结果高度一致：大量traffic/activity变化不等于critical-path周期变化。它还意味着以后做GPU shared-cache机制之前，可以先问：
> 在给定parallel-scan几何与容量下，连Belady式理想policy最多还能省多少traffic？该traffic差又有多少可能暴露成time？

如果policy-independent headroom本身很小，就不该再做replacement predictor；如果traffic bound大但timing oracle小，则问题更可能在progress/scheduling/pipeline而不是replacement。

来源：
- https://arxiv.org/abs/2609.10515

### 1.4 2026新工作进一步挤压了“泛化prefetch / 泛化内存管理”新颖性

AAAI 2026已有L2-oriented asynchronous KV prefetch：在计算窗口预取KV到L2，报告H20上的attention/end-to-end收益。PRESERVE此前已经做model-weight/KV prefetch并把预取算子插到通信隐藏窗口。ISCA 2026的SMOOTH则在on-device LLM上做fine-grained on-chip block allocation、preloading与early reclamation，用硬件辅助动态管理scratchpad。

因此以下表述不宜再作为候选创新：
- “提前把KV放进L2”
- “利用空闲带宽预取下一批数据”
- “细粒度预加载+提前回收on-chip buffer”
- “模型权重只读，所以可以提前搬”

若要继续预取方向，必须有更具体的剩余能力，例如：**batch-1 quantized decode中，已证明存在真实idle service window、下一权重tile可预测且prefetch不会被立即驱逐/争带宽，并且强软件/PRESERVE类图优化无法覆盖该执行约束**。当前没有这组证据，不优先。

来源：
- Asynchronous KV prefetch, AAAI 2026: https://ojs.aaai.org/index.php/AAAI/article/view/39224
- SMOOTH, ISCA 2026 program/author abstract: https://www.iscaconf.org/isca2026/program/
- PRESERVE见LR02/LR03历史笔记。

### 1.5 MoE“路由局部性/专家复用”已非常拥挤，不宜作为下一主候选

ISCA 2026 Best Paper“Patterns Behind Chaos”对4个200B–1000B MoE、24k+请求做data-movement-centric profiling，并从时间/空间规律指导wafer-scale设计与expert placement；Oracle-MoE（ICML 2025）和ReMoE（ICML 2026）都直接通过改变routing提高跨token expert locality/reuse。KTransformers（SOSP 2025）和2026 CPU–GPU hybrid serving工作又覆盖了expert deferral、CPU/GPU异步调度等系统路径。

所以我们已有Q30/DeepSeek/OLMoE路由与warp几何数据仍有价值，但“发现expert temporal reuse→缓存/预取专家”已不是空白。除非现有三lineage出现与上述工作不同、且强软件无法消除的硬件级访问/翻译/局部性限制，否则不建议重开深抓。

来源：
- Patterns Behind Chaos, ISCA 2026: https://ieeexplore.ieee.org/document/11617553/
- ReMoE, ICML 2026: https://proceedings.mlr.press/v306/zhu26ab.html
- Oracle-MoE, ICML 2025: https://proceedings.mlr.press/v267/zhou25b.html
- KTransformers, SOSP 2025: https://doi.org/10.1145/3731569.3764843

### 1.6 一个值得独立screen的新近视角：batch-1 decode的“利用率假象”与固定fragment浪费

IISWC 2026论文/预印本“Dissecting GPU Utilization for LLM Inference on Nvidia Hopper”指出：单一SM utilization会把fragment fill、occupancy、stall、wave quantization与kernel selection混在一起。它特别强调small-row decode GEMM的固定GMMA fragment填充率问题，并用多视图NCU counter解释低batch decode的有效利用率。

它的平台是H100/Hopper+BF16 GMMA，不能直接平移到RTX4080/AWQ W4 kernel；但**方法非常值得移植**：对C16不要再问“这个kernel是不是memory-bound/SM busy多少”，而是把当前Ada W4 decode拆成：
- useful tile/CTA fill
- achieved occupancy vs kernel resource ceiling
- long-scoreboard/other stalls
- wave/CTA supply
- L2/DRAM service
- launch/granularity gap

这可以从既有NCU/launch/timeline先做CPU-only映射，只有缺某个决定性counter时才补最小109 profile。

来源：
- https://arxiv.org/abs/2609.12923

## 2. 当前最值得并行推进的三个窗口

### W1：Merged gate/up strong-baseline guard（高优先级，CPU-only）

问题：当前two-stream结果无论正负，都必须知道标准merged gate_up路径能否在**同Qwen2.5 AWQ语义**下成立；否则我们容易把runtime缺失的标准优化误判成研究机会。

先做源码/格式审计，不用GPU：
- 当前AutoAWQ checkpoint gate/up qweight/qzeros/scales能否无损拼成一个merged linear；
- vLLM当前Qwen2 + AutoAWQ/Marlin如何装载gate/up两个logical shard；
- 合并后W4 kernel、reduction、SiluAndMul是否与当前逐算子数值语义匹配；
- 哪些差异属于强baseline，哪些会改变kernel/dataflow/数值合同；
- 只有可比性闭合才准备未来109小基线。

STOP：如果merged path已经是成熟、语义匹配且平台可运行的强baseline，则plain gate/up concurrency不作为新机制，只保留为当前runtime诊断。

### W2：PASCAL policy-independent cache-headroom screen（高优先级，CPU-only）

问题：对已有C16 split/grouped GEMM、必要时DTC cache候选，先算“任何replacement policy最多还能救多少shared traffic”，再决定还值不值得做cache机制。

只消费已有静态/trace/CTA映射：
- 识别是否满足parallel/shared cyclic scan近似；
- 构造N/M/C/phase或可替代的progress-gap描述；
- 计算TTL/LRU bound与policy-independent residency bound；
- 与已有actual L2 miss/DRAM traffic比较；
- 把“traffic oracle gap”和“timing oracle gap”分开；
- 若Belady式traffic headroom已小，关闭replacement方向；
- 若traffic大但time headroom小，转向progress/scheduling，不做replacement predictor。

这个窗口的价值不是复现PASCAL论文，而是把其“先算policy-independent upper/lower bound”的方法变成我们自己的cache实验gate。

### W3：Ada W4 decode utilization multi-view screen（中高优先级，先CPU-only）

问题：我们的low-batch W4 decode究竟被哪一种“利用率缺口”主导，而不是用memory-bound/compute-bound二分法。

先消费现有：
- FFN timeline
- E1 semantic NCU
- AWQ RAW/M256/M1 traffic
- grouped/split native结果
- kernel launch/CTA/grid/block信息

建立角色级表：
projection / attention / reduction / elementwise

至少区分：
- CTA/wave supply
- active warp与资源上限
- long scoreboard
- tensor/core path
- L1/L2/DRAM traffic
- launch gap
- kernel selection/shape transition

若已有证据能说明瓶颈，STOP；只有一个决定性视图缺失时，生成最小NCU contract，不能重新做完整profiling campaign。

## 3. 暂不优先的方向

1. **generic KV/L2 prefetch**：AAAI 2026/PRESERVE/SMOOTH近邻过强。
2. **generic intra-GPU concurrent scheduling**：NanoFlow/Bullet/Resonator已覆盖；必须有新的具体resource/semantic limitation。
3. **MoE expert locality/cache**：Patterns Behind Chaos/ReMoE/Oracle-MoE已经非常靠近。
4. **generic fusion/megakernel**：vLLM merged projections、Mirage/MPK、ComFuse等已覆盖大量能力。
5. **继续M1F**：项目内部headroom/cost已经否决，无需借新论文复活。
6. **继续dequant-result cache**：项目内部whole-decode headroom已否决，StreamDQ/QUICK/FLUTE等近邻也不支持重开。

## 4. 下一轮判据

统一使用：

现象
→ strong-software/current-system nearest neighbor
→ policy/compute/oracle headroom
→ only-if-needed native diagnostic
→ realizable mechanism
→ oracle-gap explanation

特别对cache方向增加一层：

static/shared-scan geometry
→ policy-independent traffic bound
→ actual traffic gap
→ timing exposure bound
→ replacement/scheduling/dataflow归因

避免再次出现“miss/traffic减少很多→默认周期也会大幅改善”的误判。

## 5. 阅读等级

本轮取得并核读：
- PASCAL arXiv HTML正文（核心§1–4及关键定理/评估说明），从LR10“摘要-only”升级。
- vLLM Qwen2与AutoAWQ当前公开源码/文档，作为strong-baseline capability核查。
- NanoFlow OSDI 2025、Bullet ASPLOS 2026、Resonator ISCA 2026公开论文/会议摘要。
- SMOOTH ISCA 2026公开作者摘要/会议信息。
- AAAI 2026 asynchronous KV-cache prefetch公开论文摘要。
- Patterns Behind Chaos ISCA 2026公开论文摘要/Best Paper信息。
- ReMoE/Oracle-MoE PMLR正文入口与摘要。
- Dissecting GPU Utilization for LLM Inference on Nvidia Hopper arXiv/IISWC公开摘要。

未运行任何作者artifact；没有把H100/H20/GB10结果直接当成RTX4080数值；没有用系统论文证明C16某机制有效。
