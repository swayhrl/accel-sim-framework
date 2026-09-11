# C13 effective-config audit — Path A

状态：`CONDITIONAL_PATH_A_ONLY`

仅当 umbrella Goal `C13_EFFECTIVE_CONFIG_AUDIT_GOAL.md` 的 E0 审计已经证明：实际执行 geometry / config path / launcher provenance 与 intended experiment matrix 不一致时进入本路径。

本路径目标不是“把结果修成预期”，而是：

> 精确隔离错误执行点，保留原始证据，修复执行 provenance，并以最小 replay 重新获得 intended geometry 下的可审结果。

## A0. 冻结旧证据

所有原 C13 raw logs 保持 immutable。任何被证明跑错 geometry 的 arm：

- 不删除；
- 不覆盖；
- 不改 raw SHA；
- 状态改为 `INVALID_FOR_SCIENTIFIC_COMPARISON_WRONG_EFFECTIVE_GEOMETRY` 或更精确的等价标签；
- 在 `FAILURE_RETRY_AUDIT.md` 记录 intended vs actual geometry、根因、raw SHA、旧结果为何不能继续使用。

不要把 execution mistake 写成 architecture failure。

## A1. Root-cause closure

必须定位到具体工程原因，例如：

- campaign runner row/path 复用；
- stale generated config；
- command manifest 与实际 argv 不一致；
- duplicate-option folding错误；
- wrong binary/runtime path；
- output-dir误绑定；
- config generation模板继承错误；
- 其他有直接证据的原因。

修复必须最小化，并增加自动防回归检查：

1. launch 前保存实际 command receipt；
2. 保存实际 config SHA；
3. 独立 option-folding effective-geometry receipt；
4. arm metadata中的exact entries/Segment/Lseg必须与receipt一致，否则拒绝启动；
5. output-dir不得复用旧invalid attempt。

## A2. 先做 equivalence control，不直接重跑 candidate

第一优先运行：

`C13-EQ-P320S10-C12BIN`

- Prefill
- C12 binary/core
- MANUAL
- exact320
- Segment N8
- Lseg10
- no exclusion
- frozen C12 trace/registration/PA

该控制点必须与 C12 Prefill F7-L10 做全量等价审计：

- full-ROI cycles；
- 692 per-kernel cycles；
- L1/L2 TLB；
- Segment attempts/hits/suppressions；
- PTW/PTE；
- requester latency；
- KERNEL telemetry。

如果不能解释/复现 C12 F7-L10，不得继续按照 Path A 假定只是 launcher bug；立即转入 Path B。

## A3. 识别受影响范围

基于根因精确判断旧 C13 哪些 arm 受影响：

- selective Prefill pair；
- selective Decode pair；
- L8/L9/L11；
- CAP-P320；
- CAP-P768S10。

禁止因为发现一个bug就机械重跑全部9点。

只重跑 effective config 被证明错误或无法确认的点。

## A4. Selective H1 最小重跑

如果问题仅影响 Prefill selective pair：

1. 重新生成 fresh exact320/no-exclusion same-new-binary control；
2. 先要求该control与正确的exact320 baseline/equivalence anchor一致；
3. 再运行 exact320 + exclusion candidate；
4. candidate只能与同一binary、同一geometry control比较。

若Decode旧pair已经通过 actual-config审计且结果自洽，不重跑Decode。

必须重新报告：

- cycles；
- L2 misses/walks/PTE DRAM/requester latency；
- Segment hits/suppressed；
- kernel691；
- Embedding/Output、FFN、Attention Projection；
- per-kernel cycle closure。

## A5. H2/H3 selective retention

如果 E0 证明 H2/H3 configs实际正确：保留其原结果。

如果同一launcher/config bug影响H2/H3：仅重跑受影响点，并在旧结果旁保留 superseded provenance。

Fine latency的最终结论只能使用已确认 geometry 的实测点。

Capacity 2×2只使用已确认 A/B/C/D geometry 的点。

## A6. 输出

在：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT/`

至少生成：

- `PATH_A_ROOT_CAUSE.md`
- `INVALIDATED_ARM_AUDIT.tsv`
- `EFFECTIVE_CONFIG_MATRIX.tsv`
- `EQUIVALENCE_CONTROL.tsv`
- `RERUN_STATUS.tsv`
- `SUPERSEDING_C13_RESULTS.tsv`
- `FINAL_REPORT.md`

最终必须对H1/H2/H3分别标：

- `ACCEPTED_AFTER_PATH_A_REPAIR`
- `UNCHANGED_ACCEPTED`
- `SUPERSEDED_BY_PATH_A_RERUN`
- `UNRESOLVED`

成功状态：

`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`

普通launcher/parser/resource问题主动解决并继续；资源管理沿用C13 adaptive admission。