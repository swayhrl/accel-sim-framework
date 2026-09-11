# C13 diagnostic window — START HERE

状态：`C13_UNDER_EFFECTIVE_CONFIG_REVIEW`

C13 minimal diagnostics 已完成 9/9 arms，但 ChatGPT final review 发现 Prefill effective-configuration / profile-equivalence 异常：`C13-SEL-P10-CTRL-NEWBIN` 虽声明 exact320 + Segment N8 + Lseg10，却与 `C13-CAP-P768S10` 的 full-ROI 与关键 translation telemetry 呈现高度异常的 bit-exact identity，而正式 C12 Prefill F7-L10 exact320 与两者显著不同。

因此当前优先任务不是继续设计新架构，也不是直接接受/否定 selective policy，而是先闭合 effective-config correctness。

Framework diagnostic branch：

`hrl/vm-m4b-c13-diagnostics-v0`

C13 final evidence commit：

`90e7b46736d75c402abd58fd67323098aa0353cf`

正式 C12 closeout：

`a268aba0d01310294074ded5bb8017e2092394c0`

建议继续使用独立 worktree：

`/workspace/worktrees/accel-sim-vm-m4b-c13-diagnostics`

## 当前必须按顺序阅读

1. `C13_EFFECTIVE_CONFIG_AUDIT_GOAL.md`
2. `C13_EFFECTIVE_CONFIG_PATH_A_WRONG_EFFECTIVE_GEOMETRY.md`
3. `C13_EFFECTIVE_CONFIG_PATH_B_MANUAL_PROFILE_CORRECTNESS.md`
4. 原 `C13_DIAGNOSTIC_EXPERIMENT_MATRIX.tsv`
5. 原 `C13_DIAGNOSTIC_ACCEPTANCE.md`
6. `C13_ADAPTIVE_ADMISSION_ADDENDUM.md`（仅在审计确认需要 replay 时使用）

## 当前审查边界

- 原 9 份 C13 raw logs 全部保留 immutable；不得覆盖。
- 不先假定只有 H1 出错。因为 C13 L8/L9/L11 与 H2 capacity arms 也通过 `FAIR_ARM_MANUAL` 表达诊断 geometry，umbrella audit 必须证明 MANUAL + 显式 geometry 与对应 C12 profile 的功能等价性。
- 不先宣布 H2/H3 无效；只有审计证明同一问题影响这些点时才 quarantine。
- E0 先纯只读重建 actual command / config / effective options / fair-arm source semantics；只有证据不足或路径要求时才允许最小 replay。
- umbrella Goal 将自动选择 Path A 或 Path B，用户无需中途确认。

## 两条条件路径

### Path A

如果证明 actual command、config path、effective geometry 或 launcher provenance 与 intended matrix 不一致：

`C13_EFFECTIVE_CONFIG_PATH_A_WRONG_EFFECTIVE_GEOMETRY.md`

目标是隔离错误点、保留旧证据、修复 launcher/config provenance，并只重跑最小受影响 arms。

### Path B

如果 command/config/effective option 都证明 intended geometry 正确，但 MANUAL/profile 或 new-binary default-off equivalence 仍失败：

`C13_EFFECTIVE_CONFIG_PATH_B_MANUAL_PROFILE_CORRECTNESS.md`

目标是闭合 Core/config correctness，先用最小 C12-binary MANUAL control 区分 MANUAL-profile问题与 new-binary default-off问题，再决定最小重跑范围。

## 原 C13 科学目标（历史上下文）

C13 originally tested：

1. object-selective Segment eligibility；
2. exact-remainder capacity × Segment interaction；
3. fine Segment latency around prior break-even。

这些结果当前处于 effective-config review 状态；正式 C12 fair matrix 不受影响。

成功状态由 umbrella Goal 决定：

- `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`
- `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_B_READY_FOR_REVIEW`

真正无法继续：

`C13_EFFECTIVE_CONFIG_AUDIT_HARD_BLOCKER_WITH_EVIDENCE`
