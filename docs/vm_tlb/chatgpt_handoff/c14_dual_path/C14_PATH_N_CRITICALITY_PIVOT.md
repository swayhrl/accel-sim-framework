# C14 Path N — translation criticality / exposure pivot

状态：`AUTHORIZED_EXPLORATORY_PATH`

## N0. Scientific question

C12 已经出现一个稳定但未闭合的问题：translation slow-path事件可以大幅减少，而端到端性能收益却很小，甚至随lookup latency增加转负。因此替代问题是：

> 不是“能不能减少更多 TLB miss / walk”，而是“哪些 translation latency 真正暴露到 GPU 执行关键路径，哪些 miss 大部分被并行性隐藏？”

若 Segment 最终被证明收益脆弱，这条路线可独立成为主方向；即使 Segment 最终成功，这条路线也能解释为什么某些 operator/phase 不敏感。

## N1. Source-level exposure audit

从 C12 Core `57bb71...`梳理 translation requester 与 memory pipeline 的连接点，至少回答：

1. request何时因translation pending而不能进入后续memory pipeline；
2. 一个translation完成后，request何时真正issue到cache/interconnect；
3. translation等待期间是否常有其他warp/request可填满issue slot；
4. 当前`requester_translation_latency_cycles_total`统计的是“request latency”，还是“真正暴露 stall”；
5. translation MSHR merge是否让多个request latency重复计算；
6. 哪些结构有能力定义“translation是当前唯一阻塞原因”。

输出：

- `PATH_N_EXPOSURE_AUDIT.md`
- `PATH_N_CRITICALITY_OBSERVABLES.tsv`

## N2. Instrumentation design

在 Core branch：

`hrl/vm-m4b-c14-criticality-v0`

优先做**观测而非机制**。所有instrumentation default-off，开启时不改变timing。

建立至少两层指标：

### Tier 1 — directly measurable exposure

尽可能统计：

- requester translation pending cycles；
- translation completion → memory issue gap；
- memory issue opportunity存在但被translation pending阻塞的cycles；
- LSU / memory-stage因为translation而无法service head request的cycles；
- translation完成当cycle是否立即释放一个可issue request；
- pending translation requester count / high-watermark；
- per-kernel/per-object/per-operator可归因的exposed cycles。

### Tier 2 — conservative criticality proxy

如果无法严格证明“全GPU critical path”，定义并清晰命名proxy，例如：

`TRANSLATION_HEAD_BLOCKED_CYCLE`

要求：

- 必须有明确局部结构定义；
- 不得命名为`critical_path_cycles`除非真的证明；
- 不得把request latency直接等价为exposed stall。

建议区分：

- L1-TLB hit
- L2-TLB hit
- Segment hit
- PTW/PTE
- merged request

## N3. Conservation / correctness

至少建立：

- exposure cycle不能为负；
- `exposed <= pending`（若定义支持）；
- completion-to-issue sample count与eligible completion数守恒；
- per-kernel sum闭合到ROI/micro总数；
- default-off binary行为与C12 baseline一致；
- instrumentation-on不得改变cycles（确定性micro test必须bit-exact）。

若某个counter为了采集不得不改变调度顺序，则该设计`NO_GO`，换更保守观测点。

## N4. Microdiagnostics

使用`C14_MICRODIAGNOSTIC_MATRIX.tsv`中的N类点。

重点比较：

- Prefill vs Decode；
- FFN vs Attention Projection vs Embedding/Output；
- translation-heavy但cycle不敏感的kernel；
- Segment低延迟收益明显的kernel；
- Segment activity很多但timing不变/接近不变的kernel。

要回答：

1. request translation latency高的kernel是否真的exposed stall高？
2. Decode大量slow-path suppression为什么只有小性能收益，是否因为exposure本来就低？
3. Prefill/Decode差异是miss数量、parallelism，还是exposure程度不同？
4. Embedding/Output kernel691是否是高translation-latency同时高exposure，还是仅总工作量大？

## N5. Candidate mechanisms — only after instrumentation signal

最多形成两个设计草案，不要求本Goal完成full implementation：

### N-CAND-1 — exposed-request priority

如果少量translation request贡献大部分exposed stall：

- 在walker/PWQ/MSHR/L2-TLB arbitration中优先这类request；
- criticality信号必须来自硬件可实现局部信息，不允许使用oracle kernel labels作为最终机制。

### N-CAND-2 — latency-hiding-aware deprioritization

如果大量translation miss几乎不暴露stall：

- 避免把资源平均花在所有translation；
- 允许将walker/PWC/lookup资源优先给当前head-blocked / low-slack request。

仅输出机制规格、state bits、更新时机、复杂度，不自动开full-ROI。

## N6. Go/No-Go

### GO

至少满足：

- requester latency与exposed stall明显解耦；
- exposed stall高度集中于少数request/kernel/operator；
- Prefill/Decode有稳定不同的exposure结构；
- proxy可以用局部硬件状态实现，而不是oracle。

### NO-GO

- 几乎所有translation latency都同等暴露；
- 无法在不改变timing的前提下观测有效proxy；
- exposed stall与已有requester latency完全等价，没有新增信息；
- criticality只能依赖kernel/operator oracle标签。

## N7. Deliverables

- instrumentation patch/tests in criticality Core branch
- `PATH_N_REPORT.md`
- `PATH_N_INSTRUMENTATION_AUDIT.md`
- `PATH_N_MICRO_RESULTS.tsv`
- `PATH_N_GO_NO_GO.md`
- 如有signal：`PATH_N_CANDIDATE_DESIGNS.md`

所有结果必须标注`EXPLORATORY_MICRODIAGNOSTIC`或`SUPPORTED_CANDIDATE_SIGNAL`，不得直接称paper mechanism。