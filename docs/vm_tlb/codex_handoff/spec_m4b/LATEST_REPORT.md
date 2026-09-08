# Window C — SPECULATIVE M4B DEVELOPMENT current handoff

Status: `C12_C5_FULL_ROI_FAIR_PERFORMANCE_AUTHORIZED_AGGRESSIVE_PARALLEL` / `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`.

C11 has passed review and closed the full-ROI prefill/decode1 provenance gate. C5 full-ROI execution is authorized under C12。当前追加授权允许在不改变科学语义的前提下更激进并行：两个 F0 继续运行时，可猜测性提前启动其他独立 arms；早跑结果必须经过 F0 后 promotion audit 才能晋升正式 PASS。

## 冻结 C11 execution identity

- C11 evidence closeout: `a082f73ad752bbf9beb630ede036d80ecf266f35`
- Runtime/config functional anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- Linked binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- Prefill trace-list: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` (692 entries)
- Decode1 trace-list: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` (740 entries)
- PA contract: `C5_MODELED_PA_HIGH_UNUSED_BIT_V1`, explicit `MODELED_DRIVER_PA`, common across fair arms for each ROI.

## 当前授权 Goal

`C12_C5_FULL_ROI_FAIR_PERFORMANCE_REPLAY`

必须阅读并执行：

- `docs/vm_tlb/codex_handoff/spec_m4b/C12_C5_FULL_ROI_FAIR_PERFORMANCE_GOAL.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_ACCEPTANCE_MATRIX.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_RESULT_SCHEMA.tsv`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_AGGRESSIVE_PARALLEL_ADDENDUM.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_AGGRESSIVE_PARALLEL_ACCEPTANCE.md`
- C11 review pack，尤其 `C5_ARM_MATRIX.tsv`、`C5_COMMAND_MANIFEST.tsv`、`C5_ACCEPTANCE_MATRIX.md`、`COMMON_PA_FAIRNESS_VALIDATION.tsv`。

Primary matrix 不变：22 点 = F0/F1/F2/F5/F9 + F7/F8 的 Lseg 5/10/20，两个 ROI 各 11 点。

## 激进并行覆盖规则

- 不停止当前健康 F0；
- 立即目标总 simulator 并发 `6-way`；
- 6-way 连续至少 5 分钟资源 GREEN 后允许试 `8-way`；
- 资源压力时自动 8→6→4→2 降级；
- 允许 F0 未完成时提前运行 P1/P2/P3 独立 arm；
- 早跑 arm 状态先为 `SPECULATIVE_EARLY_EXECUTION_PENDING_BASELINE_GATE`；
- 两个 F0 PASS 后做 identity/terminal promotion audit；
- 每 arm 必须有 ROI+arm+lseg 唯一锁，禁止同一 output dir 两个真正 simulator owner；
- 单 arm 失败只隔离/重跑该 arm，不杀其他健康 worker；
- 任何模拟语义 identity 修改仍触发原 C12 全矩阵 invalidation 规则。

执行优先级仍用于调度优先而非阶段依赖：P0 → P1 → P2 → P3。只要有空闲 worker slot，可从优先队列取下一个独立未跑 arm。

Goal 必须继续至 22/22 terminal PASS，除非证明真正 architecture/provenance/correctness blocker。资源等待、普通工程错误、单 arm crash 不是最终停止条件。

禁止运行 F6/F3/F4/H0、KV segmentation、12K、M5，禁止修改 Window A/B。

最终状态：

- `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`
- `C12_C5_HARD_BLOCKER_WITH_EVIDENCE`
