# C12 / C5 全负载公平性能实验 Goal

状态：`AUTHORIZED_TO_START_AFTER_PREFLIGHT`

本轮正式授权执行 C5 full-ROI 公平性能矩阵。C11 已通过 review：输入、共同 non-identity modeled PA、公平臂配置、命令与验证工件均已闭合。

本轮目标不是继续改架构，而是回答：

> 在约 66Kbit 的相近翻译存储预算下，传统 exact TLB、Sub-entry、physical PWC、Weight Segment 以及 Segment+Sub-entry，谁在完整 Prefill/Decode ROI 上性能更好，为什么？

## 0. 冻结执行身份

Framework branch：`hrl/vm-m4b-speculative-v0`

C11 evidence closeout：`a082f73ad752bbf9beb630ede036d80ecf266f35`

冻结的 functional/config execution anchor：

`d64408a97d76a320a6d49468653d416e33677af8`

Core：

`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

Linked binary SHA-256：

`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`

Prefill full ROI：692 kernels；trace-list SHA-256：

`a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`

Decode1 full ROI：740 kernels；trace-list SHA-256：

`b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`

C11 registration hashes：

- prefill：`6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`
- decode1：`3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`

PA contract：`C5_MODELED_PA_HIGH_UNUSED_BIT_V1`，显式 `MODELED_DRIVER_PA`，不是实测硬件 PA。

所有 primary arms 在同一 ROI 必须使用完全相同的 driver PA mapping。

## 1. 执行前强制 preflight

先阅读并逐项复核：

- C11 `FINAL_REPORT.md`
- C11 `C5_ARM_MATRIX.tsv`
- C11 `C5_COMMAND_MANIFEST.tsv`
- C11 `C5_ACCEPTANCE_MATRIX.md`
- C11 `COMMON_PA_FAIRNESS_VALIDATION.tsv`
- 本轮 `C12_ACCEPTANCE_MATRIX.md`

必须重新执行 C11 static input validator，并确认：

- 22/22 primary point 存在；
- 全部 config SHA 与 C11 matrix 一致；
- 两个 trace-list SHA 一致且所有 trace entry 存在；
- 两个 registration SHA 一致；
- binary SHA 一致；
- Core/Framework functional anchor 一致；
- H0 不在任何 command 中；
- F6 不在 primary 22 点中；
- C5 output root 尚不存在，或如果这是本轮自身经过审计的失败尝试，则按失败隔离规则处理。

任一 hash 不一致时，禁止启动该 arm，先查明原因。

## 2. 22 点正式矩阵

每个 ROI 共 11 点：

- F0：exact-768，66,000 bits；正式 baseline。
- F1：Sub-entry G96，59,802 bits；`REFERENCE_APPROX_SUBENTRY_16`。
- F2：exact-688，59,125 bits；与 F1 的近预算 exact comparator。
- F5：physical PWC 120 + exact-656，64,745 bits。
- F9：exact-656，56,375 bits；F8 的 no-Segment comparator。
- F7：Segment N8 + exact-320，65,300 bits；Lseg = 5/10/20。
- F8：Segment N8 + G32，57,734 bits；Lseg = 5/10/20；`REFERENCE_APPROX_SUBENTRY_16 + SPECULATIVE_CANDIDATE`。

两个 ROI：prefill / decode1。

总计：22 点。

F6 2MiB 继续作为未执行 diagnostic；不在本轮 primary matrix。F3/F4/H0 不执行。

## 3. 优先级与分阶段执行

Goal 连续执行，不需要每一阶段回来问用户。

### P0：基线与资源校准

先跑：

- prefill F0
- decode1 F0

允许 2 路并行。两个 F0 都必须 terminal PASS，之后才能形成正式 speedup baseline。

用 `/usr/bin/time -v` 记录每个 arm peak RSS / elapsed time。

### P1：最有信息量的核心矩阵

在 F0 PASS 后，优先完成每个 ROI：

- F2
- F5
- F7-L10
- F8-L10
- F9

加上两个 F0，共 12 个核心点。

这些点优先回答：

- physical PWC 与 exact baseline 的比较；
- Segment-only 的收益；
- Segment+Sub-entry 的收益；
- F8 vs F9 的 Segment 增量；
- F1/F2 之外，是否已经出现明显候选方向。

### P2：Segment latency sensitivity

随后补：

- F7-L5 / F7-L20
- F8-L5 / F8-L20

两个 ROI，共 8 点。

### P3：Sub-entry-only

最后补两个 ROI 的 F1。

最终必须 22/22 全部闭合，不能因为中间趋势明显就省略后续点。

## 4. 激进但安全的并行策略

A 已完成，B 冻结，本轮 C 是唯一正式重负载主线。继续尊重共享 lock：

`/workspace/vm_tlb_post_terminal_heavy_slot.lock`

C 获取一次 lock 后，一个 C parallel batch 可以内部多 arm 并行；batch 完成后释放。

首次 P0：2-way。

根据 P0 实测单 arm peak RSS `P`，计算：

`N_mem = floor((MemAvailable - 32GiB) / (1.5*P + 2GiB))`

实际并发：

`N = min(N_mem, physical_core_headroom, 6)`

默认建议：

- GREEN 且内存充足：4-way；
- 实测 RSS 很低、PSI/IO 持续健康：最多 6-way；
- YELLOW：降到 2-way；
- RED：不启动新 arm，保留已完成 evidence，等待恢复。

资源门采用实际吞吐而不是要求 swap delta 严格为 0：

GREEN：

- MemAvailable >= 32 GiB
- memory PSI full <= 1%
- io PSI full <= 2%
- iowait <= 10%
- swap-in/out <= 4 MiB/s

YELLOW：

- MemAvailable 20–32 GiB，或 memory PSI 1–3%，或 io PSI 2–5%，或 swap 4–16 MiB/s

RED：

- MemAvailable < 16 GiB
- memory PSI full > 5%
- io PSI full > 8%
- iowait > 25%
- swap-in/out > 16 MiB/s 连续两个窗口

资源等待不是 final failure。禁止 busy-spin，禁止操作 A/B/其他用户进程。

## 5. 每个 arm 的 terminal gate

一个 arm 只有同时满足以下条件才可记为 PASS：

1. simulator exit = 0；
2. processing kernel markers = immutable kernel-list entries；
3. telemetry kernel records = expected entries；
4. terminal quiescence / exact-once checks PASS；
5. PTE request/response conservation PASS；
6. object attribution conservation PASS；
7. Segment/Sub-entry/PWC 对应 arm-specific invariants PASS；
8. config/trace/registration/binary hashes 与 manifest 完全一致；
9. raw run log 和 `/usr/bin/time -v` sidecar 保存；
10. parser 输出 schema 完整。

Prefill expected kernels = 692；Decode1 = 740。

每个 arm 一结束就立即解析和验收，不要等 22 个全部跑完再发现坏数据。

## 6. 必须保存的结果指标

### 性能

- `gpu_tot_sim_cycle`
- `gpu_tot_sim_insn`
- `gpu_tot_ipc`
- speedup / slowdown relative to **同 ROI 的 C5 F0**

禁止直接把 A/C4 generic/ideal 数字当成本轮 baseline；C11 后 PA backend 与 binary identity 已变化。A 结果只能作为历史 characterization，不可与 C5 数值直接混算。

### TLB / translation

- L1/L2 TLB accesses/hits/misses/miss rate
- L2 TLB evictions/replacement
- port stalls
- MSHR allocations/merges/full/wait/lifetime/high-watermark
- walker/PWQ
- requester total/max latency
- PTE requests/responses/L2-only/DRAM/memory wait

### PWC

- accesses/hits/misses/evictions
- level breakdown
- queue/port wait/high-watermark

F5 必须验证其 physical PWC 120-entry geometry，而不是 legacy logical PWC。

### Segment

- lookup attempts/hits/misses/fallbacks
- descriptor-covered accesses
- L2/PTW suppressed/avoided counts
- lifecycle/replica correctness
- Lseg sensitivity
- common PA agreement

### Sub-entry

- group hits/misses
- sibling/subentry occupancy/coverage
- replacement
- stale/generation discard

### Cache / memory cross-layer

- L1D / L2 object-aware outcomes
- L2 replacement
- L2 queue pressure
- interconnect/DRAM latency and queue statistics
- PTE 与 data traffic 的可观测分层

## 7. 关键比较必须显式计算

至少形成以下比较：

- F1 vs F2：Sub-entry-only vs near-budget exact。
- F5 vs F0：physical PWC vs near-66K exact baseline。
- F7-L10 vs F0：Segment-only 主候选 vs baseline。
- F7 L5/10/20：Segment latency sensitivity。
- F8-L10 vs F9：在相近低预算下隔离 Segment 增量。
- F8-L10 vs F1：Combined vs Sub-entry-only。
- F8 L5/10/20：Combined latency sensitivity。
- Prefill vs Decode：同一机制收益与瓶颈差异。

不要只看 IPC；每个性能差异都要回到 translation / PTE / queue / cache / DRAM 指标解释。

## 8. 失败与修复规则

普通 path/script/parser/run-dir/launcher 问题必须主动修复后继续。

如果某个 arm resource-killed/OOM：

- 保存 failed attempt；
- 降并发；
- 重新跑该 arm；
- 不影响其他已验证 PASS arm。

如果只是 parser bug，且 raw log 完整、immutable：

- 可以修 parser 后重新解析；
- 不需要重跑 simulator；
- parser version/hash 必须更新并记录。

如果需要修改任何会影响模拟语义的：

- Core source；
- C5 config；
- registration；
- trace-list；
- binary；

则**所有使用旧 identity 的已完成 C5 arm 都必须标为 INVALIDATED_BY_IDENTITY_CHANGE**，移入旧 evidence 区，不得与新 arm 混合；修复后重新 full-link、冻结新 hash，并从 F0 重新启动完整矩阵。

不能为了保住已跑时间而混合两个 binary/config identity。

## 9. Final review pack

生成：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/`

至少包含：

- `FINAL_REPORT.md`
- `ARM_STATUS.tsv`
- `ARM_RESULTS.tsv`
- `SPEEDUP_SUMMARY.tsv`
- `TRANSLATION_MECHANISM_SUMMARY.tsv`
- `LSEG_SENSITIVITY.tsv`
- `CROSS_LAYER_SUMMARY.tsv`
- `PROVENANCE_MATRIX.tsv`
- `RESOURCE_HISTORY.tsv`
- `FAILURE_RETRY_AUDIT.md`
- `PAPER_FACING_FINDINGS.md`

`PAPER_FACING_FINDINGS.md` 要把内容分为：

- `MEASURED_FULL_ROI_FACT`
- `SUPPORTED_MECHANISM_SIGNAL`
- `UNRESOLVED`

不得把机制相关性写成已证明因果。

## 10. Scope guard

本轮禁止：

- KV segmentation；
- 12K 扩展；
- M5；
- 新 architecture；
- F6/2MiB diagnostic；
- 修改 Window A/B；
- 用 C5 结果回头调 PA mapping；
- 根据中途性能选择性停止不利 arm。

## 11. Goal 最终状态

成功时：

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`

真正无法继续的 architecture/provenance/correctness blocker：

`C12_C5_HARD_BLOCKER_WITH_EVIDENCE`

资源等待、单 arm crash、普通工程问题都不是 final stop 条件。