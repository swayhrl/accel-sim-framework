# C13 minimal diagnostic experiments — Goal

状态：`AUTHORIZED_TO_START_AFTER_PREFLIGHT`

## 0. Scientific objective

C12 已证明：F7 Segment 的端到端收益对 Lseg 极敏感；Operator-aware Deep Dive 又证明这种敏感性在 Transformer layer 的 FFN / Attention Projection 上跨 16 层重复出现，同时 Prefill 的若干 aggregate 结果被 final Embedding/Output kernel 691 强烈影响。

本轮不直接设计“大而全”的新 TLB，而是用最少的新 replay 回答三个高价值假设：

### H1 — Object-selective Segment

Prefill 中 `EMBEDDING_OUTPUT` 在 F7/F8 的 Lseg=5/10/20 实测点均退化，而 direct FFN / Attention Projection 在低延迟点普遍改善。假设：

> 若仅让 Transformer-layer Weight 使用 Segment，而让 Embedding/Output 对应 Weight range 继续走 conventional exact TLB/PTW，Prefill 在 Lseg=10 附近可能由负收益转为正收益；Decode 的响应可能不同。

这是待验证假设，不允许在运行前写成结论。

### H2 — Exact-remainder capacity decomposition

F7 为 fair budget 使用 `Segment N8 + exact-320`。Prefill 虽有约 48–50M Segment hits / L2 suppressions，但传统 walks/PTE-DRAM 仍高于 F0。假设：

> Prefill 的额外传统 walk 主要来自 exact remainder 从 768 缩到 320 后的非 Segment / 未覆盖 translation capacity pressure，而不是 Segment hit 路径本身无效。

用 Prefill 2×2 中缺失的两个诊断点补齐：

- exact-768, Segment off：已有 C12 F0；
- exact-320, Segment off：C13 新点；
- exact-768, Segment N8, Lseg=10：C13 新点；
- exact-320, Segment N8, Lseg=10：已有 C12 F7-L10。

这组不是 equal-budget paper comparison，而是 capacity × Segment 的 diagnostic factorial。

### H3 — Fine-grained latency bracket

Deep Dive 基于 5/10/20 三点做区间内经验插值：Prefill full-ROI break-even 约 8.75，Decode 约 10.83。假设：

> 在当前 F7 并发查询实现和同一 workload 上，细粒度实测会在 Prefill 8–9 cycle、Decode 10–11 cycle 附近出现符号翻转。

C13 只补最有信息量的点，不做 6–11 的全扫描。

---

## 1. Frozen references

正式 C12 Framework closeout：

`a268aba0d01310294074ded5bb8017e2092394c0`

C12 functional/config anchor：

`d64408a97d76a320a6d49468653d416e33677af8`

Core：

`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

C12 linked binary SHA-256：

`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`

Prefill trace-list：692 entries，SHA-256：

`a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`

Decode1 trace-list：740 entries，SHA-256：

`b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`

PA contract：`MODELED_DRIVER_PA / C5_MODELED_PA_HIGH_UNUSED_BIT_V1`。

Deep Dive accepted reference：

`8801f2e9fea4e0df1d79853a5e4440c4da463486`

Deep Dive 只提供动机、kernel/operator mapping 和诊断目标；不得用其派生结果替换 C13 自己的 full-ROI replay evidence。

---

## 2. Preflight

在独立 C13 worktree 中：

1. fetch `hrl/vm-m4b-c13-diagnostics-v0`、C12 source branch、operator-aware branch；
2. 核对 C13 branch base 包含 `a268aba0...`；
3. 核对 Core / linked binary / trace-list / C12 registrations；
4. 读取 C12 `FINAL_REPORT.md`、`PROVENANCE_MATRIX.tsv`、`ARM_RESULTS.tsv`；
5. 读取 Deep Dive `FINAL_REPORT.md`、`SEGMENT_BREAK_EVEN.tsv`、`KERNEL_CRITICALITY_FINDINGS.md`、`PWC_TRADEOFF_AUDIT.md`；
6. 审计当前配置是否已能独立设置：Segment enable/N、exact L2 TLB entries、Lseg；
7. 审计 selective Segment eligibility 是否可以**不改 Core/binary**地由现有 registration/manifest/input path 表达。

普通路径、parser、run-dir、权限问题必须主动解决，不能直接报 hard blocker。

---

## 3. Execution plan

Primary diagnostic matrix 固定为 7 个新 full-ROI points，详见 `C13_DIAGNOSTIC_EXPERIMENT_MATRIX.tsv`。

### P0 — Config-only diagnostics first

在不修改 Core / binary 的情况下优先准备并执行：

- Prefill F7-like Lseg=8；
- Prefill F7-like Lseg=9；
- Decode1 F7-like Lseg=11；
- Prefill exact-320 / Segment off；
- Prefill Segment N8 + exact-768 / Lseg=10。

这些点必须使用 C12 linked binary，保持 trace 和 modeled PA mapping 不变。

其中 capacity 两点允许 storage budget 不同，因为它们是诊断点；结果必须明确标 `DIAGNOSTIC_NON_EQUAL_BUDGET`。

### P1 — Selective Segment eligibility audit and execution

目标：对 Embedding/Output 对应 Weight range禁用 Segment eligibility，但 conventional exact TLB/PTW 仍使用同一 modeled PPN。

优先顺序：

1. 若现有 input/registration path 可表达 selective eligibility，则保持 C12 Core 和 binary 不变，生成新的 eligibility artifact，并严格证明 VA→modeled-PPN mapping 与 C12 相同；
2. 若现有路径不能表达，才允许在独立 C13 Core branch 增加最小、default-off、config-gated selective eligibility 支持；
3. 若修改 Core/binary，则 C12 F7-L10 不能直接作为唯一性能 comparator，必须额外执行 Prefill 和 Decode1 的 same-new-binary F7-L10 control，然后再与 selective candidate 比较。

Primary selective points：

- Prefill：F7-like N8 + exact320 + Lseg10 + exclude Embedding/Output Weight range；
- Decode1：同样策略，用于判断是否存在 phase-dependent response。

禁止用 kernel index 691 作为 eligibility 规则。Primary selective policy 必须来自可审计的 Weight parameter/object range。

### P2 — Per-arm validation and immediate parsing

每个 arm 一结束立即：

- terminal validation；
- raw-log hash；
- full-ROI performance；
- translation/PTE/PWC/Segment telemetry；
- 使用 frozen Operator-aware kernel map 做 read-only per-kernel/operator attribution；
- 重点检查 kernel 691 及 direct layer 0–15 FFN / Attention Projection。

不要等所有点跑完才解析。

---

## 4. Required comparisons

### H1 selective

若保持 C12 binary：

- `SEL-P10` vs C12 Prefill F7-L10；
- `SEL-D10` vs C12 Decode F7-L10。

若使用新 binary：

- `SEL-P10` vs `SEL-P10-CTRL-NEWBIN`；
- `SEL-D10` vs `SEL-D10-CTRL-NEWBIN`。

必须同时报告：

- full-ROI cycle delta；
- kernel 691 cycle delta；
- Embedding/Output aggregate；
- FFN / Attention Projection aggregate；
- Segment hits/suppressions减少了多少；
- conventional L2 TLB miss/walk/PTE-DRAM是否变化。

### H2 capacity factorial

Prefill 四点：

- A：F0 exact768 no Segment（existing）；
- B：C13 exact320 no Segment；
- C：C13 exact768 + Segment N8 L10；
- D：F7-L10 exact320 + Segment N8（existing）。

至少显式计算：

- B-A：纯 exact capacity 缩小的 measured effect；
- C-A：在不牺牲 exact capacity 时增加 Segment 的 measured effect；
- D-B：在 exact320 条件下增加 Segment 的 measured effect；
- D-C：在 Segment N8/L10 条件下 exact768→320 的 measured effect；
- 2×2 interaction term：`(D-B) - (C-A)`，只作为 diagnostic interaction，不宣传成普适因果定律。

重点检查 global walks/PTE-DRAM、Embedding/Output、OTHER_COMPUTE 和 direct layers。

### H3 latency

新增点与 existing C12 F7-L5/L10/L20 合并：

- Prefill：L5 / L8 / L9 / L10 / L20；
- Decode：L5 / L10 / L11 / L20。

必须用实测值回答：

- Prefill L8/L9哪一侧为正收益；
- Decode L11是否已经转负；
- Deep Dive 8.75/10.83 的 interpolation 是否被新点支持、修正或否定；
- 不得继续用旧插值替代新实测。

---

## 5. Resource and scheduling

C12 已无 simulator 在运行。C13仍需保守使用共享机器资源：

- 初始最多 2-way full-ROI replay；
- 观察单 arm RSS、PSI、iowait 后允许 4-way；
- 不建议超过 4-way，除非此前 C12 资源模型和实时监控都明确 GREEN；
- resource kill 只隔离该 attempt，降低并发并重试，不影响已 PASS 结果；
- 不操作其他项目/其他用户进程。

Selective implementation audit、config generation、parser/postprocess 可以与健康 simulator 并行，只要不造成明显 I/O/内存压力。

---

## 6. Evidence language

最终报告分层：

- `MEASURED_C13_DIAGNOSTIC_FACT`
- `SUPPORTED_C13_MECHANISM_SIGNAL`
- `DIAGNOSTIC_INTERACTION_ONLY`
- `UNRESOLVED`

禁止：

- 把 selective bypass 的一次正收益直接叫“最终架构”；
- 把 non-equal-budget capacity arms与 C12 fair matrix混为同等级比较；
- 把 operator/kernel cycle attribution直接写成唯一因果；
- 把 modeled PA 当真实硬件 PA；
- 根据中间性能结果改变 primary 7 点定义。

---

## 7. Review pack

生成：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_MINIMAL_DIAGNOSTICS/`

至少包含：

- `FINAL_REPORT.md`
- `ARM_STATUS.tsv`
- `ARM_RESULTS.tsv`
- `PROVENANCE_MATRIX.tsv`
- `LATENCY_FINE_SWEEP.tsv`
- `CAPACITY_FACTORIAL.tsv`
- `SELECTIVE_SEGMENT_RESULTS.tsv`
- `OPERATOR_DIAGNOSTIC_DELTAS.tsv`
- `KERNEL691_DIAGNOSTIC.tsv`
- `FAILURE_RETRY_AUDIT.md`
- `CHANGED_FILES.md`

Codex handoff：

`docs/vm_tlb/codex_handoff/c13_diagnostics/LATEST_REPORT.md`

Final report 必须明确回答：

1. selective Embedding/Output bypass 是否改善 Prefill，Decode 是否同向；
2. Prefill extra walks是否主要由 exact320 remainder capacity pressure支持；
3. 新 L8/L9/L11 实测如何修正旧 break-even；
4. kernel 691在 selective/capacity实验下是否仍是主导热点；
5. direct FFN/Attention Projection layer-wide行为是否保持；
6. 下一步应该进入 object/phase-aware hybrid mechanism，还是先补别的诊断。

成功状态：

`C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW`
