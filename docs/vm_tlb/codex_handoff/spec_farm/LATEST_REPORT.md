# Window B：SPECULATIVE EXPERIMENT FARM 当前交接

状态：`SPECULATIVE_DIAGNOSTIC`。B6 为低资源 partial closeout；B7/B8 已完成 analysis-only synthesis/prioritization。没有将任何结果合入或传播到 Window A。

## 隔离与来源

- Framework branch：`hrl/vm-spec-farm-v0`
- B8 evidence SHA：`3c5700cba44739a9abb2470c863d1942c20e1079`
- Core branch 起点：`0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- B simulator binary SHA-256：`2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`
- B scratch：`/workspace/vm-spec-farm/`
- Window A touched：NO

## 已有证据边界

- B1：prefill `134/692`、decode1 `96/740`，均为 `REAL_PARTIAL`。
- B2：37/54 单-kernel smoke 已完成，仍有 17 `MISSING`。
- B3/B5：仅 planned geometry；不是 runtime result。
- B4：BFS/Hotspot/SRAD 仅 static compatibility。
- B7：0 `REAL_PASS`、2 `REAL_PARTIAL`、37 `SMOKE_ONLY`、38 `PLANNED_ONLY`、12 `STATIC_ONLY`、17 `MISSING`；522 项提取/守恒检查通过。
- B8：建立 6 个可证伪假设和 18 个最小信息实验 bundle；第一执行层为 E01--E10。B8 没有运行实验。

B8 review pack：
`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B8_CROSS_WINDOW_HYPOTHESIS_AND_EXPERIMENT_PRIORITIZATION/`

## 外部 A checkpoint（只读支持证据）

A progress-review checkpoint：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`。

七个 A C3 arms 已 terminal，`prefill-paper` 在 checkpoint 时仍运行。A 的 decode terminal evidence 显示 ideal/disabled 相同，generic/paper 有显著 translation overhead；paper 虽减少部分 TLB miss/MSHR-full 指标却仍比 generic 慢。该结果只用于要求未来 B 实验保留 queue/stall/latency observables，不与 B 数值合并，也不替代 B-local controls。

## 当前资源/执行边界

B 当前不恢复 worker。B6/B7 接受的资源 gate 保持：候选 job class 先有 peak-RSS 校准；有效并发 1；启动前不得存在持续 swap；iowait 可接受；`MemAvailable > max(4×peak, 最近波动+2×peak)`；常规 `20% + 4 GiB` 恢复线仍有效。

## B9 authorized next stage

下一阶段：

`B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT`

模式：`ANALYSIS_ONLY / STATIC_PREFLIGHT`。

B9 只把 B8 的 E01--E10 固化为未来可执行的 exact command/config/trace/observable/resource/result contract。禁止 simulator、worker、build、trace generation、full-ROI scan 或真正运行 E01--E10。

严格执行：
- `docs/vm_tlb/codex_handoff/spec_farm/B9_MINIMUM_EXPERIMENT_EXECUTION_PREFLIGHT.md`
- `docs/vm_tlb/codex_handoff/spec_farm/B9_ACCEPTANCE_MATRIX.md`

B9 最终只能选择：
- `EXECUTION_PACK_READY_AFTER_A_TERMINAL`
- `PREFLIGHT_BLOCKED_CONFIGURATION_MISMATCH`
- `PREFLIGHT_NEEDS_USER_DECISION`

完成后 commit/push 并 STOP，不自动启动任何实验。
