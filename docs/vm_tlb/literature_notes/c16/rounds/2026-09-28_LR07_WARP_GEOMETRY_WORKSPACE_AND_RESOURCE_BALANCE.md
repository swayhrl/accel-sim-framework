# C16 LR07：warp请求结构、临时工作区与并行度的交互

日期：2026-09-28。维护：ChatGPT。

状态：`LITERATURE_REVIEW_AND_BOUNDED_EXPLORATION_DESIGN`。本轮没有执行GPU、模拟器、作者artifact或node164 raw重算，没有读取Lane4 partial结果。下述任务的状态是可下发/排队，不是已运行或已获得新科学结果。

## 0. 从已有总账出发

读取文献分支README（本轮起点`dc41de767b55f3ba1532627f1cb5dc176ea539ee`），以及工作总账`hrl/c16-work-history-audit-20260928-v1`。不重开已关闭的E1干预、覆盖/算子族扩展、E3、host加速或split-factor调优矩阵。

目前主比较仍由Lane4决定；Lane7已下发OLMoE多输入、6-session routing provenance任务，不能被本轮候选插队或修改。现有三模型MoE的weight/input约各半是active-lane address-event观察，不是硬件流量分摊。上一轮split8→split1只有up_proj M256明显改善，全局H1不成立。以上结论保持不变。

本轮留下两件事：

1. **Lane8 / 174-new / CPU-only：**利用已保存C16WARP1记录检查每条warp访存的重复地址、字节并集和sector覆盖；不需要新采集。
2. **Lane7 / 109 / 排在当前OLMoE之后：**一个新的split8/split1×访存预处理状态诊断，区分局部执行变化是否依赖预热状态；不扫描更多split参数。

## 1. 原文阅读登记

| ID | 完整题名 | 本轮阅读范围 | 适用边界 |
|---|---|---|---|
| P1 | cuThermo: Understanding GPU Memory Inefficiencies with Heat Map Profiling | arXiv:2507.18729 HTML；§IV方法/采集字段、§V–VI相关案例 | 二进制动态profiling；主要限于同thread block的共享结构；未运行工具 |
| P2 | FlashDecoding++: Faster Large Language Model Inference on GPUs | arXiv:2311.01282 HTML；§4 flat-GEMM、§5硬件适配数据流 | 并行度/带宽的形状适配已有先例；不是C16 AWQ相同实现 |
| P3 | FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving | arXiv:2501.01005v2；§3及附录D/E | attention/KV与动态调度；不能直接当AWQ replacement baseline |
| P4 | QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving | arXiv:2405.04532 HTML；§3及§5相关设计/资源分析 | 量化方法和kernel共同改变，不是只换kernel的AWQ对照 |
| P5 | Stream-K: Work-centric Parallel Decomposition for Dense Matrix-Matrix Multiplication on the GPU | 原始摘要及作者论文页面；正文获取未成功 | 只用于确认已有work-centric partitioning近邻，不冻结实现合同 |
| D1 | CUDA C++ Best Practices Guide，Coalesced Access to Global Memory | NVIDIA官方当前网页相关章节 | 32B事务模型是访问结构说明；不替代当前runtime实测 |
| D2 | Nsight Compute Profiling Guide，Memory Workload Analysis / Quantities | NVIDIA官方当前网页相关章节 | request、sector、wavefront、cache miss与DRAM必须分开；不升级本项目NCU版本 |

本轮新增四篇的相关正文阅读；P5仍是摘要/作者页面，不写成五篇全文精读。MARLIN/QUICK/FLUTE/SpecMD/MonoNN已在LR06登记，不重复计数。

## 2. 作者做了什么；对C16意味着什么

### P1 cuThermo：同样访问次数，可能是不同共享结构

**原文：**作者使用访问某个word/sector的distinct warp数，而不只统计地址热度；NVBit记录PC、addr[32]、访问宽度、mask、访问类型和CTA/warp身份，分析同一CTA内共享。默认指定一个CTA采样，不能因此保证全kernel代表性。[P1]

**我们的新问题：**当前三lineage已统计per-shard footprint和lane-event组成，但未把每个warp记录里的lane地址一起做并集合并。输入可能是广播，权重可能是连续或分散读取；两类lane事件同量，sector覆盖未必同量。

这不是重新发明coalescing，也不是重建cuThermo。先读已有raw，用几百MB以内的CPU流式处理判断下一问题是否存在。高度广播也可能说明硬件已经有效合并，不能将重复lane计数当可再消除的DRAM流量。

### P2 FlashDecoding++：形状适配不是新的独立贡献

**原文：**flat-GEMM在tile宽度、数据复用和CTA数量间权衡：较宽N tile可提高算术强度，却减少CTA供给；不同N区间采用不同资源侧重点。其attention部分另有数值保护机制，不进入本项目实验。[P2]

**我们的判断：**继续扫描split=1/2/4/8/16只会接近常见kernel调优。值得另问的是当前split改变的临时结果和访存状态，是否会改变并行度收益的适用条件。不能只按M选策略，也不能仅凭CTA数预测时间。

### P3 FlashInfer：中间结果可以按CTA资源预算，而不必按逻辑分片总数

**原文：**附录D区分不需要切分的短任务直接写最终结果，和切分任务的partial/reduction；workspace组织与CTA数关联。其计划/运行分离还服务于动态负载和固定执行接口。[P3]

**我们的判断：**为分片分配了多少scratch、实际访问了多少、何时再次用到，是不同问题。不能把allocation字节全当cache驻留，但也不能只把reduction kernel自身的流量当scratch全部代价。注意这是attention的设计，不是现成可替换当前AWQ的机制。

### P4 QServe：没有大量DRAM访问也可能受片内指令吞吐限制

**原文：**W4A8KV4设计将量化与GPU数据流一起考虑，关注CUDA-core上的反量化/转换、数据布局和硬件资源比例；其数值表示与当前W4A16 AWQ不相同。[P4]

**我们的判断：**后续不能从“DRAM降了很多”直接推出“已接近计算峰值”。不过LR06已筛过反量化布局问题，本轮不再立即开一条大后端移植线；只将CUDA/LDST/解码吞吐作为解释候选，等明确证据再升级。

### P5 Stream-K：仅确认近邻，不冒充实现阅读

原始摘要提出按总inner-loop工作量划分，而非只按固定输出tile划分GPU工作。[P5] 这足以约束我们不把工作量切分本身称为创新；本文完整同步、缓存与实现合同本轮没有读到。

## 3. 新任务A：从lane事件到warp地址覆盖（174-new）

### 3.1 已有raw足够做什么

实际读取了accepted三lineage consumer：

- commit：`08536be9940590be101c7f5bac2117ba82056db5`
- `util/vm_tlb/c16/three_lineage_consumer/recompute.py`
- `docs/vm_tlb/chatgpt_handoff/c16/three_lineage_moe_consumer_v1/ANALYSIS_CONTRACT_V1.md`
- OLMoE `c16warp1_v39_common.h`。

C16WARP1的每条280B记录保存static index、active mask、CTA xyz、warp及32个地址。三个accepted bundle合计594,944条warp记录。既有consumer逐lane累计role和unique地址，没有形成本轮的同record byte-union/sector-fanout统计。

**限制：**记录没有直接保存访问宽度，必须从该lineage的精确static operand/path authority恢复，不能由BF16 tensor推断指令宽度。transport sequence也没有写入C16WARP1，故不能拼跨shard的全局时间顺序。

### 3.2 分层计算

G0：不需要访问宽度，计算active lanes、不同起始地址、重复起始地址比例。

G1：仅在访问宽度/path语义合格的记录上，令：

- `L`：各active lane访问宽度之和（重复字节也计）；
- `U`：**同一条动态warp访存记录内部**地址区间的字节并集；
- `S`：覆盖这些区间的不同32B sector数；
- `C=32*S`：sector覆盖字节proxy。

报告`L/U`、`U/C`以及每条record的S分布；按lineage、role、opcode/width、CTA分组。不能把C称为实际L2/DRAM bytes。

**纯示例，不是C16测量：**32个lane各读4B，若全读同一地址，则L=128、U=4、C=32；若连续读128B，则L=128、U=128、C=128。lane事件数相同，数据需求和sector覆盖不同。前一种低U/C伴随有效广播，并不自动是坏合并。

G2：资源许可时，追加**同shard、同CTA**的每sector distinct-warps描述；不拼不同进程绝对VA，也不从共享次数推导复用间隔或cache命中。

### 3.3 为什么值得独立做

原T3问题是模型/实现共性；Lane6是token级路由时间相关性；本任务是kernel内部请求结构。这些不是同一份结果换名字。若只是常见GEMV广播，记录`FAMILIAR_BROADCAST_WITH_NO_NEW_OPPORTUNITY`也有价值，不强行设计新cache。

## 4. 新任务B：split-K收益与访存预处理状态交互（109，排队）

### 4.1 直接来自既有raw的增量线索

源：`0e88faa28c9066b48e394dce657d7a16e6332a32`，pack `C16_LOWBIT_SPLITK_NATIVE_AB_109_V1`。

根据`LAUNCH_AUDIT.tsv`计算（MiB=2^20 bytes）：

| M256点 | split8 scratch | split1 scratch |
|---|---:|---:|
| up_proj | 74 MiB | 9.25 MiB |
| down_proj | 14 MiB | 1.75 MiB |

同pack `NCU_UP_M256_KERNEL_ROWS.tsv`提供：

| up_proj M256 | L2 bytes | DRAM bytes | profiler duration ns |
|---|---:|---:|---:|
| A GEMM | 1,158,028,384 | 103,424,128 | 637,216 |
| A reduction | 107,549,408 | 75,175,296 | 119,200 |
| B GEMM | 910,524,608 | 301,312 | 549,472 |

**算术分解，不是新实验：**A与B的总L2差355,053,184B中，247,503,776B来自GEMM行之差，不只是删除的reduction。总DRAM差178,298,112B中，103,122,816B来自GEMM行之差。故“全部收益只是少一个reduction kernel”解释不完整，但这些总量仍不能指认weight/input/scratch各贡献多少。

候选解释并列：工作分割改变访存复用、scratch压力改变缓存状态、CTA供给/同步变化。仅凭74MiB allocation大于某容量不能证明capacity cliff。

### 4.2 与上一轮的不同

固定相同A/B实现，不加split值、不换backend、不改数学。只增加一维明确的execution-state preparation：

- `WARM_SAME_ARM`：每个sample前执行同arm预热；
- `EVICT_CONDITIONED`：同样预热，再访问独立的大缓冲区，随后测目标。

对up/down M256形成8个cell，一次GPU campaign完成计时和限定NCU。conditioner不计入目标计时，不影响输入/权重；不能把evict-conditioned命名为已证明的全冷cache。

如果A/B差异随准备状态明显变化，得到的是state-conditioned split-policy observation；如果变化不明显，也应关闭这条解释而不扩大参数扫描。这不是重新做E1驻留干预矩阵，更不是更改Lane4。

### 4.3 排队边界

当前OLMoE multiround Goal先完成并发布、释放GPU锁；本任务随后才能在Lane7同窗口的新worktree执行。不得重启或修改当前OLMoE任务。

若当前Goal因model/runtime/GPU正确性发生未解决阻塞，队列不自动绕过阻塞。若只是正常无信号或EOS早停，不把科学负结果当设备错误。

## 5. 本轮不启动的候选

- QServe式W4A8后端替换：数值格式/算法改变，当前不能作为纯kernel对照。
- FlashInfer整套attention系统迁移：范围过大，且C16已有repeat-K/MLA typed证据需先回读，不能重复抓。
- cuThermo整套新NVBit采集：已有warp raw可先分析，不新增工具链。
- 更广MoE temporal模型扫描：等当前OLMoE provenance结果，不从post-hoc lag11继续扩机制。
- 所有M1F/strong-baseline/full-reuse-window timing：仍由Lane4 gate决定。

## 6. 参考来源与阅读定位

[P1] https://arxiv.org/abs/2507.18729 ; https://arxiv.org/html/2507.18729 （IV-A/IV-B/IV-C）

[P2] https://arxiv.org/html/2311.01282 （§4–5）

[P3] https://arxiv.org/html/2501.01005v2 （§3、Appendix D.2/D.3/E）

[P4] https://arxiv.org/html/2405.04532 （§3、§5相关段落）

[P5] https://arxiv.org/abs/2301.03598 ; https://mgarland.org/papers/2023/streamk/ （摘要/作者页面；正文未取得）

[D1] https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html （Coalesced Access to Global Memory）

[D2] https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html （Quantities及MemoryWorkloadAnalysis）

注意D1/D2是本次查询时的官方网页，接口使用仍以项目已接受的安装版本为准。没有从网页版本号推断node109已升级。

## 7. 下发与维护

详细任务置于独立coordination分支`hrl/c16-lr07-exploration-coordination-v1`；本notes不包含执行完成声明。

任务安排：Lane8@174-new现在可下发；Lane7@109新诊断排在现有OLMoE之后。两者均不依赖Lane4 partial。完成后先review commit/pack/raw，再往总账追加完成记录；目前只记`READY_TO_DISPATCH`与`QUEUED_NOT_STARTED`。
