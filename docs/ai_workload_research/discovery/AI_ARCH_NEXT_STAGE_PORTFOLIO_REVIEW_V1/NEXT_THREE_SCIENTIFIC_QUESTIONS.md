# 下一阶段三个科学问题与最小实验合同

**PROPOSAL_NOT_AUTHORIZED / NO_GPU_PROBE_READY**。本文件只提出条件式实验，不授权设备、下载、GPU 或新机制。依据见 [组合台账](AI_ARCH_RESEARCH_PORTFOLIO_STATUS.md)、[论文排除](RECENT_LITERATURE_AND_SOFTWARE_EXCLUSION.md)、[决策](AI_ARCH_NEXT_STAGE_DECISION.md)。

先冻结数据、数学语义、实际版本、完成工作、计时及资源边界；外部资格满足后可在一个获准连续任务中完成资格、原生对照、诊断和归档，无需再拆准备 Goal。下列规模由识别变量决定，不设任意完整仿真次数上限。本 Goal 不执行矩阵。正式样本与局部诊断分池，全部正负样本保留。

## Q1：3DGS 晚期暴露等待由 CPU 生产、软件调度还是 GPU 服务限制？

**PRIMARY；缺完整可恢复晚期状态与匹配数值合同。** 依据 [GS 冻结审查](evidence/GS_FROZEN_EVIDENCE_REVIEW.json)。

### A. 科学假设及反证

H_CPU：全局扫描、实际 Adam 更新及转发生产滞后于 GPU，线程/布局策略可解释主要等待。H_GPU：较强兼容软件之后仍有进入完整关键路径的 GPU 服务或传输限制。允许二者共存。

A44 已接受的主线程候选区间并集是约 14.084/14.746ms，不能再用旧跨线程 30.871/32.128ms 当硬件收益上界。CPUAdam 57.746/64.779ms、参数转发 41.855/45.489ms 存在并行/嵌套，不能直接相加；GPU 先结束和正 CPU tail 支持调查生产端，不证明纯 GPU 空闲。

反证：合法线程/放置或兼容软件消除等待并改善完整已完成更新时间，记 SOFTWARE_ABSORBED；区间改变而应用时间不变，不能认定有收益；observer 扰动或未 drain 的 deferred 更新造成差异，应修观测；必须改变 Adam/更新顺序/质量才能获益，属于不同算法语义。

### B. 最强适用软件基准

原 GS-Scale 已接受 Rubble 路径，包括真实 deferred optimizer/epsilon 近似规则；在同一获准 cpuset/NUMA 下比较可解释的线程策略。作者请求 64 线程，A26GR1 OMP_THREAD_LIMIT=16，不能假称作者 64 性能复现；A46 terminal Torch 64 也不能被写成 Torch 总是 1。

CLM 的 camera reuse/cache、CPU 调度和 optimizer overlap 是直接软件反证，只有保持同样更新/质量合同的功能才能进入同语义基准。TideGS eviction 后 optimizer cold restart、camera 重排和部分固定规模不增密实验单列质量-吞吐 Pareto，不能无损替换。A45H 合成 U=N 数组性能不是自然训练收益。

### C. 独立信息量诊断

从同一完整状态做 observer OFF/修复 ON 配对，保持 camera IDs、RNG、更新数和结束 drain。登记 step/线程/stream/转移关联；同一 host monotonic 时钟求主线程等待并集，worker sync、CPUAdam、转发分别报告累计与并集。未建立合法时钟关系不将 CUDA-event 与 host 纳秒相减。

选取真实进入 GPU 的数据做独立服务时间诊断，区分“尚未生产”和“已就绪但服务慢”；移除 optimizer 的局部 replay 不算完整训练加速。CPU 记录 visited/matched/updated rows、scan 次数、U/N，SH 实际非零 numel/bytes 及唯一 storage。调用 SH D2H 不保证有 payload；不同 camera 不保证没有 Gaussian reuse。

### D. 独立输入资格

主输入仍为合法 Rubble，保持原 SH/LR/densification/reset schedule，refine_stop=15000。14900–15200 的 N 稳定不证明参数或 stable IDs 稳定，不得提前禁用增密制造固定图。

完整状态须包括 Gaussians/稳定身份、Adam moments/计数、CPU/GPU 转发和 pending/deferred 梯度、RNG、loader/camera cursor、调度、源码/输入 SHA 与恢复数值检查。现有 splat-only 不满足，最后 pending gradient 不能丢弃。没有完整 checkpoint 不能声称恢复。

发现/调优与保留 camera 窗口预分割；独立验证保持真实自然训练。第二场景只有许可、完整状态、自然输入和容量都合格才增补；缺少时不宣称跨场景。不得自动重训 15000 步创造状态。

### E. 应用成本和物理资源

分母为完成相同真实更新工作的 wall time，窗口主体与最终 drain/flush 分列，不能把未完成梯度移到窗口外。声称训练收益另需同质量/收敛对照；短晚期窗口不证明 time-to-quality。

记录真实 CPU 扫描/更新、核心/线程拓扑、传输 bytes、关键路径、GPU kernel 服务、同步；主存/链路计数仅在已有合法权限下采集。已有 sampled RSS 26,337,488,896B，约 24.53GiB，不能继承 Qwen 16GiB 上限。未来草案 host 48GiB、own NVML 14GiB、累计 GPU 1800s；完整状态磁盘按验收大小 S 加工具/日志≤2GiB，需资源所有者确认，不是当前授权。

### F. 创新碰撞

GS-Scale 已扩展 CPU/GPU 异步更新，CLM 已优化 cache/order/overlap，TideGS 已管理超大工作集及 optimizer residency，GSArch 已提出缓冲/过滤/bank 布局。GSArch 只有摘要方法可核，不引用其加速比作本机证据。泛称异步 CPUAdam/camera reuse/冷热缓冲不足为新意；须找到强软件之后具体可控的残余。

### G. 最小矩阵

| 配置 | 控制与样本 |
|---|---|
| T8/T16/T64-request | 相同完整状态、camera 序列、cpuset/NUMA、数学路径及 drain；每策略 3 个独立恢复短窗口，区组交错。T64 仅在主机所有者许可且能解释实际线程/核心映射时执行，否则 NOT_AVAILABLE |
| 较强策略 observer OFF/ON | 同状态独立恢复，3 对配对窗口，与正式样本分池 |
| 一个真实输入 GPU 服务诊断 | 同实际算子/数据/条件，有界观测，不替代完整训练 |
| 保留 camera 窗口 | 策略预冻结，3 个独立恢复区组，不根据验证结果再调参 |

普通晚期候选 [15150,15200) 为 50 steps；[15050,15200) 才是 150，[15100,15200) 是 100。真实 checkpoint 不支持时，执行前依据合法可恢复 schedule 冻结新窗口，不能伪造状态或改训练语义。不无限扫描线程数。

### H. STOP 或转向

完整状态、恢复身份、适用数值容差或主机/CPU 放置权限缺失即 STOP_STATE_OR_NUMERIC_AUTHORITY，不占 GPU。CPU fixture 容差不能直接成为训练容差。软件解决则关闭硬件方向；只有不同 optimizer/质量合同有效则转独立算法提案。原 observer 修复前后 Gaussian 轨迹不同，不得当性能配对。

## Q2：动态 KV/Hybrid State 是否存在强软件之后的容量与迁移成本？

**SECONDARY；SOURCE_ONLY，尚无完整模型/自然状态轨迹/质量/设备资格。** 依据 [Hybrid/MoE 审查](evidence/MOE_HYBRID_AUTHORITY_REVIEW.json)。

### A. 科学假设及反证

自然 multi-turn/prefix branch/resume/eviction 下，GDN recurrent/conv checkpoint 与 full-attention KV 的生命周期产生现有 pool/alias/reuse/flush 无法隐藏的真实容量或迁移等待，进入完整请求成本。

若只是同 storage alias 重复计数、被现有策略覆盖、只有理论内容而无物理分配/时延变化，或必须改变质量/输入/调度才能获益，假设被否定。容量增长不直接证明带宽饱和。

### B. 最强适用软件

源锚 Qwen3.5-4B@851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a，24 GDN+8 full-attention，只是 config 来源，不是已验收全权重/native 后端。选择一个确实兼容的固定运行时：vLLM mixed page/coordination 或 SGLang pools/checkpoints/ownership/alias/reuse，按实际运行版本验证。**不能拼接 UnifiedMambaPool 与其禁用的 linear ReplaySSM。**

ReplaySSM ring/flush、Strata I/O/layout/scheduler 已覆盖泛化想法。ACL HybridKV 是有损视觉 KV，不是 GDN 管理器，也不是 exact baseline；更改 state precision/近似的配置必须单列质量-成本语义。

### C. 独立诊断

一个真实支持且保持 exact 语义的 checkpoint/prefix reuse OFF/ON × 应用 state-pool budget ample/near-capacity，2×2。容量档由真实 allocation 转折确定，不能按 49MiB 内容公式设定或用外部显存压力任务制造竞争。

相同请求到达、分支、flush、scheduler、生成规则；cold/warm/hit/miss 分段记录，不以人为重复 prompt 冒充自然命中。若没有安全同语义开关，执行前改成唯一可识别的合法 policy 对照并记录识别力下降，不杜撰 API。可加一个 flush 边界局部诊断，不扫全部参数。

### D. 独立输入资格

实际合法权重/scale、tokenizer/template、结构/runtime SHA，BF16 weights/FP32 state 以真实实现为准。冻结 model-facing tokens、多轮/分支/恢复/淘汰轨迹和许可，预分发现与保留会话。独立验证先用不同自然会话/生命周期，不为凑数新增模型。

Qwen2.5 A00/A01 不等于 Qwen3.5 已接受输入；provider cache usage、shape replay、合成重复 prefix 不等于真实 token/state。核实 state orientation、position、ownership、flush endpoint；适用数值/质量参考在 GPU 前建立，不能借旧 Qwen logprob 阈值。缺失则 NO_NUMERIC_AUTHORITY。

### E. 成本及资源

49.125MiB/sequence recurrent+conv、full-KV 32768B/token、约 1572 tokens 交叉点是结构推导，**不是 allocation/流量/wall 实测**。记录 unique storage 内容、pool/reserved/物理 NVML、host mirror/checkpoint/ring/workspace/Graph、实际 eviction/restore/flush bytes 与时间、TTFT/ITL/完整请求及完成数/质量。

独立物理资源为容量、主存驻留、迁移链路与服务开销。控制仅用应用自身公开 allocator knob，不改全局时钟/功率/他人任务。未来草案：109 SM89 native 资格通过后，own NVML15400MiB、host32GiB、GPU1800s、新 trace/cache≤4GiB；全模型现存合法资产另验，不是本轮资源授权。

### F. 创新碰撞

Strata exact KV 多层 I/O/调度，vLLM/SGLang hybrid ownership/checkpoint，ReplaySSM ring/flush 均须排除。统一 state 池、KV 迁移、共享 prefix 本身无足够新意。必须指明自然 hybrid 状态下具体不可隐藏冲突和已有接口未解决部分。

### G. 最小矩阵

| 变量 | 设计 |
|---|---|
| Exact policy | 实际支持的 reuse/checkpoint OFF/ON |
| 应用容量 | ample/接近真实自然容量转折，不制造 OOM |
| 轨迹 | 发现集和冻结保留集；同真实请求及到达 |
| 重复 | 每格 3 个独立初始化 trace replay 区组，交错；cold/warm 分开 |
| 语义 | 实际应用生成长度/停止、精度/质量规则在 GPU 前冻结，不缩短上下文求 fit |

主矩阵 4 格。相邻 token 不是独立请求重复。增加一次稳定态 allocator snapshot 和一次真实 flush/migration 诊断解释时间/容量，诊断分池。若无容量转折，记录此输入未暴露假设，不加 synthetic hotspot 强迫正结果。

### H. STOP/转向

缺真实模型/输入/许可、质量、后端、设备或状态映射即 STOP。仅有 config 保留 SOURCE_ONLY；不为矩阵下载模型、换精度或上下文。强软件覆盖则 SOFTWARE_ABSORBED；只有有损 retrieval/pruning 有效则独立算法提案，不包装为原 exact 硬件机会。

## Q3：自然路由 MoE 在强 FP8 fused 软件之后是否仍有专家访存残余？

**CONDITIONAL；A30T 仅 H200/SM90a 源候选，109 SM89 不合格。** A70O NO_SURVIVOR_IN_SEARCH_SCOPE 不是全部 MoE native 被否定。

### A. 假设及反证

自然小 batch decode 的 layer-specific 专家访问，在 tuned grouped 与 MonoMoE 后仍有可测权重/metadata 服务成本且进入完整 TPOT。不得以普通 batch 共享或慢 expert-loop 制造残余。

强软件吸收收益、仅必要单次 payload、局部 replay 改善却应用不变、只在 synthetic 热点或改变 route/精度时有效、held-out 不复现，均否定晋升。locality、低 tile 填充、平均利用率不足作证明。

### B. 最强软件基准

同一真实 FP8 checkpoint、scale/inverse、packing/layout，比较实际可用且 tuned 的 vLLM FP8 grouped 与 MonoMoE；保留 BF16 input 及内部真实量化，不拿 BF16 expert loop 当唯一基准。router_logits→output 包含 routing/top-k、专家投影/激活/combine；router projection 在 API 上游，shared expert/通信另计。online quant/pack/metadata 不能免费。

[新鲜度核查](evidence/SOFTWARE_FRESHNESS_CHECK.json)：当前/历史 wrapper 字节相同，SM90a/E256/H2048/I512/M≤8 声明未变。只核 wrapper，不证明 runtime build/JIT 或数值通过；不得调用会 JIT 的 has_monomoe 冒充只读检查。

### C. 独立诊断

捕获真实 native 的少量 activation/router logits/top-k IDs/scores、层及步骤，将相同自然 route 重放给两个后端，明确只是完整算子局部比较。expert 键为 (model,layer,expert,representation)，不能跨层合并同编号。

如需供给反事实，局部只读工作集/预置必须有真实 bytes、cache 状态、kernel 身份证据，保持数据/数值，记录实际 counter 与时延；未经测量不以 HOT/STREAM 名称证明因果。自然高低 reuse 只是观察性分组，不是独立硬件控制，不能随机造热点替代。

### D. 模型和独立验证

FP8 源锚 Qwen3.5-35B-A3B-FP8@b955db3baa2e2fe51de7455fdfa08d7c29865abd；合法完整 weights/scales/packing 核 SHA，不能以 BF16 config 代替。登记 tokenizer、自然请求、prompt/output、逐层 route、Graph/scheduler。

调优前分 discovery/held-out，保留不同自然主题/长度/路由分布，不挑好样本。旧 Q30 Layer24 prefill 的 16384 assignments/93 active experts 不是自然 B1 decode。单层 fit 不等于整模型：40 层 routed FP8 weights/scales 约 30GiB，尚未包含其它部分，不能在 4080 换弱后端冒充。

### E. 完整成本与资源

完整请求 wall/CUDA-event、TTFT/TPOT/吞吐、实际生成工作及数值/质量；局部完整 router-logits-to-output 时间、实际 DRAM bytes、metadata/index/pack/quant/launch、Graph/shape、权重/scales 读取。router projection/shared expert/通信在应用成本闭合。

理论 payload 与 counter 分开；Profiler replay 不作原生计时；必要数据请求不等于可消除成本，局部更高带宽不保证应用收益。未来需独立获准 H200/SM90a，草案 own NVML≤120GiB、host≤96GiB、GPU≤1800s、新 trace/cache≤4GiB；不是租用、下载或节点迁移授权。预算不足缩观测节点，不改模型/精度/route。

### F. 创新碰撞

MonoMoE 已融合小 batch 调度/量化/投影/combine，作者自然 TPOT 收益是软件结果。Patterns Behind Chaos 已研究 locality/placement/duplication；wafer 是仿真，实机 placement 仅 expert linears，不是请求。Not All Models Suit Expert Offloading 表明模型/输入 locality 差异，不证明强软件残余。

专家缓存/预测/融合不足构成新机制；必须找出 Mono 和现有 placement 之后具体成本、可改硬件变量及面积/功耗/容量/复杂度代价。

### G. 最小矩阵

| 项目 | 设计 |
|---|---|
| 应用 | 2 个验收后端 × B1/B4 × output1/32，共 8 格；相同自然 prompt/长度 |
| 计时 | 每格 2 warmup、5 个区组交错 formal，保留全部输出 |
| 独立验证 | 冻结策略用于 held-out，不重调布局 |
| 路由 replay | 实际主导层少量真实 decode steps，后端间同 input/logits/top-k |
| 数值 | 比较量化数学、expert 身份、token/质量；求和差异容差需独立依据且 GPU 前冻结 |

B4 在 wrapper M≤8 内仍须验证实际 Graph/shape，源码支持不等于运行通过。不扫描 B8/全部层/上下文。若两种软件无法完整请求同边界，只能给局部算子结论，不能报告完整硬件收益。相邻 token 不当独立重复。

### H. STOP/转向

无 H200 合法窗口、完整 FP8/scales、自然 route、强后端或数值合同则 SOURCE_CONDITIONAL，不能降到 SM89。counter/shape 身份缺失记 INCONCLUSIVE，不填零、不以 B1 代 B2。软件收益归 SOFTWARE_ABSORBED；只剩必要 payload 且无独立变量，NO_HARDWARE_CANDIDATE_PROMOTED。

## 共同冻结和停止规则

1. 记录实际源码/runtime/model/input SHA、许可、完成工作、数值/质量、计时、cold/warm、整批 completion 先保存；不观察结果后放宽。
2. 设备所有者确认共享协议、窗口、锁/门控和 CPU placement；本 Goal 不取锁。不得通过他人 GPU 负载或全局时钟/功率/权限制造反事实。
3. 监控进程树/cgroup、NVML、私有磁盘；保留退出进程的 censored 峰值缺口，不声称全程完整。
4. 自然时延、counter、理论流量、仿真估算分开。缺独立控制最多 MODEL_CONSISTENT/PARTIALLY_ATTRIBUTED，不升 CAUSALLY_SUPPORTED。
5. 身份/安全/资源失败清理停止对应任务；可选工具失败保留有效结果；未知数据不补造。无完整应用价值或软件已吸收则关闭候选。
6. 新硬件卡须有实际幅度、强软件残余、硬件变量、机制预测、反证、独立验证、面积/功耗/时序/复杂度代价；当前三线均未满足。
