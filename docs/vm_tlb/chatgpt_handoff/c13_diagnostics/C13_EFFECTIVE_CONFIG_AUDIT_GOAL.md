# C13 effective-config / profile-equivalence audit — Goal

状态：`AUTHORIZED_TO_START`

本 Goal 是对已完成 C13 minimal diagnostics 的独立正确性审计与条件修复，不新增新的科学假设矩阵。目标是解释并闭合一个在 ChatGPT final review 中发现的 provenance/effective-semantics 异常，然后自动进入 Path A 或 Path B，不等待用户中途确认。

## 0. 已知正式锚点

Framework branch：`hrl/vm-m4b-c13-diagnostics-v0`

C13 final evidence commit：

`90e7b46736d75c402abd58fd67323098aa0353cf`

正式 C12 closeout：

`a268aba0d01310294074ded5bb8017e2092394c0`

C12 Core：

`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

C12 binary SHA-256：

`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`

C13 selective Core：

`4f5f2a2583d71e5aee0e5ff59b67e5e6cd7d5be0`

C13 selective binary SHA-256：

`63c6011f20a22ff37afe0cef2958b67b32a9a6dcf0132d92ff28f62a8395cec4`

C13 selective Core 只应增加 default-off 的 range-gated Segment exclusion overlay；empty exclusion 必须保持 C12 行为。

## 1. 为什么要做这次审计

C13 intended matrix 明确规定：

- `C13-SEL-P10-CTRL-NEWBIN`：Prefill，Segment N8 + exact320 + Lseg10，ALL_C5_ELIGIBLE_WEIGHT；
- `C13-CAP-P768S10`：Prefill，Segment N8 + exact768 + Lseg10。

committed config / manifest 也分别声明 exact320 与 exact768。

但 accepted result 中，两者出现了高度异常的 bit-exact telemetry identity：

- `gpu_tot_sim_cycle = 62058600`
- `vm_l2_tlb_misses = 7583`
- `vm_translation_walk_starts = 2233`
- `vm_pte_dram_responses = 1926`
- `vm_translation_requester_latency_cycles_total = 1027315721`

且多个其他 counters 同样一致。

与此同时真正 C12 Prefill F7-L10（Segment N8 + exact320 + Lseg10）为：

- cycles `63370888`
- L2 misses `120919`
- walks `33749`

Decode same-new-binary control 则能够复现 C12 Decode F7-L10。

此外，C13 L8/L9、capacity B/C 都使用 `-gpgpu_vm_fair_arm 0` (`FAIR_ARM_MANUAL`) 来表达 C12 fair-arm 之外的诊断 geometry。因此本审计必须先证明：

> `FAIR_ARM_MANUAL + 显式相同 geometry` 与对应的 C12 fair-arm profile 在功能语义上等价；否则 H2/H3 也需要重新界定，而不能只修 H1。

## 2. 总原则

1. **先离线审计，后决定是否 replay。** 不允许一上来重跑 9 个 arm。
2. 当前 9 份 C13 raw log 全部冻结为 immutable evidence；不得覆盖、删除或改写。
3. C12 H2/H3/H1 结论在审计期间保持 `UNDER_EFFECTIVE_CONFIG_REVIEW`；不要先宣布 invalid，也不要继续当最终 accepted fact。
4. 普通 path / parser / manifest 问题主动解决，不等待用户确认。
5. 不干预其他项目进程。
6. 需要 replay 时继续使用 C13 adaptive admission；资源波动只调整并发。

## 3. Phase E0 — 纯只读 effective-config reconstruction

必须逐 arm 回到**实际执行证据**，而不是只看 intended matrix：

### E0.1 actual command / file provenance

对至少以下 arms：

- `C13-CAP-P768S10`
- `C13-SEL-P10-CTRL-NEWBIN`
- `C13-SEL-P10`
- `C13-LAT-P8`
- `C13-LAT-P9`
- `C13-CAP-P320`
- Decode selective control/candidate

审计：

- campaign runner 实际 argv；
- `-config` 的实际绝对路径；
- run-dir command receipt / manifest / config copy（若存在）；
- config SHA-256；
- binary SHA-256；
- Core HEAD；
- trace/registration SHA；
- eligibility artifact SHA；
- output-dir 唯一性；
- 是否存在 config path / row / environment 复用错误。

### E0.2 independent effective-option reconstruction

实现或复用一个只读 option-folding checker，按 simulator config parser 的真实“重复 option 最终值”语义独立恢复：

- `gpgpu_vm_fair_arm`
- `gpgpu_vm_l2_tlb_entries`
- `gpgpu_vm_l2_tlb_assoc`
- `gpgpu_vm_l2_tlb_mode`
- Segment enable / entries / lookup latency / map
- exclusion map
- PWC mode / entries

不得只从 `ARM_RESULTS.tsv` 抄 intended metadata。

如果 raw log / simulator startup 已打印 effective VM geometry，也必须对齐；若未打印，记录 `NOT_EMITTED`，不要猜。

### E0.3 source audit：fair_arm 是否只负责 profile 配置

对 C12 Core 与 C13 selective Core 全仓搜索 `fair_arm` / `gpgpu_vm_fair_arm` 的所有运行时使用点，明确：

- `configure_fair_arm()` 对 MANUAL/F7 的行为；
- `config.fair_arm` 是否在 controller 初始化后仍参与 lookup/fill/replacement/PTW/Segment runtime 行为；
- 是否仅用于配置校验/telemetry label；
- option parse → vm_config construction → `configure_fair_arm` → controller construction 的准确顺序。

不能因为 `configure_fair_arm(MANUAL)` 返回 true 就自动证明 MANUAL 与 F7 等价；必须审完所有使用点。

### E0.4 bit-exact equality depth

只读比较：

`C13-CAP-P768S10` vs `C13-SEL-P10-CTRL-NEWBIN`

至少检查：

- 692/692 per-kernel cycles 是否逐项完全一致；
- 关键 cumulative vm_* per-kernel deltas 是否逐项一致；
- Segment hits/attempts/suppressed；
- L1/L2 TLB；PTW/PTE；requester latency；
- KERNEL-scope cache telemetry。

如果只是 full-ROI totals 一致但逐 kernel 不同，要如实记录；如果逐 kernel / counters 也 bit-exact，更强地指向 effective-semantics identity。

输出：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT/`

至少先生成：

- `EFFECTIVE_CONFIG_MATRIX.tsv`
- `ACTUAL_COMMAND_AUDIT.tsv`
- `FAIR_ARM_SOURCE_AUDIT.md`
- `BIT_EXACT_IDENTITY_AUDIT.tsv`
- `AUDIT_DECISION.md`

## 4. 分流判据

完成 E0 后，必须在 `AUDIT_DECISION.md` 明确选择且只选择一个主路径。

### PATH A — WRONG_EFFECTIVE_GEOMETRY_OR_LAUNCH_PROVENANCE

进入 Path A，只要证明至少一项：

- actual command 使用了错误 config path；
- config/manifest row 复用错误；
- run-dir 对应的实际 config SHA 与 intended SHA 不一致；
- effective L2 entries / Segment geometry 与 experiment matrix 不一致；
- selective control/candidate 没有实际运行 intended geometry；
- 其他可证明的 launcher/config provenance 错误。

随后完整执行：

`C13_EFFECTIVE_CONFIG_PATH_A_WRONG_EFFECTIVE_GEOMETRY.md`

### PATH B — INTENDED_GEOMETRY_PRESENT_BUT_EQUIVALENCE_FAILS

如果 actual command、config hash、independent option folding 均证明 intended exact320/Segment N8/L10 确实送入 simulator，但 default-off control 仍不能复现 canonical C12 F7-L10，则进入 Path B。

Path B 还包括：

- MANUAL profile 与 F7 profile 可能存在功能语义差异；
- new selective Core empty-exclusion default-off equivalence 可能被破坏；
- vm_config 构造/覆盖顺序可能导致 nominal option 与真正 controller geometry 不一致；
- 其他 Core/config correctness 问题。

随后完整执行：

`C13_EFFECTIVE_CONFIG_PATH_B_MANUAL_PROFILE_CORRECTNESS.md`

## 5. 强制最小 disambiguation control

如果 E0 不能仅靠现有证据唯一判定，允许并优先执行**一个**最小控制点：

`C13-EQ-P320S10-C12BIN`

要求：

- C12 Core/binary；
- Prefill；
- `FAIR_ARM_MANUAL`；
- exact320；
- Segment N8；
- Lseg10；
- no exclusion；
- frozen C12 trace / registration / modeled PA。

它只用于区分：

1. MANUAL + exact320 是否能复现 C12 F7 profile；
2. 还是 new binary 的 default-off equivalence 出问题。

比较：

- 若 `C13-EQ-P320S10-C12BIN` 复现 C12 F7-L10，而 new-binary control 不复现 → 优先进入 Path B 的 `NEW_BINARY_DEFAULT_OFF` 子路径；
- 若它也不复现 C12 F7-L10 → 优先进入 Path B 的 `MANUAL_PROFILE / EFFECTIVE_CONFIG` 子路径；
- 若它揭示 config/runner 实际 geometry 与声明不符 → Path A。

不得为了省时间跳过这个控制点后直接大规模重跑。

## 6. H2/H3 保护规则

如果审计证明 MANUAL 与等价 F7 geometry 在 runtime 行为上等价，而且 C13 L8/L9/D11、CAP-P320、CAP-P768S10 的 effective configs 均正确，则 H2/H3 可保留，不重跑。

如果证明 MANUAL/profile/effective geometry 的问题会影响这些点：

- 仅将受影响行标记为 `QUARANTINED_BY_EFFECTIVE_CONFIG_AUDIT`；
- 保留原 raw logs；
- 精确列出最小需要重跑的 arms；
- 不重跑不受影响的点。

## 7. 最终 closure

无论走 Path A 还是 B，最终都必须：

- 更新/补充 C13 `FAILURE_RETRY_AUDIT.md`；
- 生成 `C13_EFFECTIVE_CONFIG_AUDIT/FINAL_REPORT.md`；
- 更新 `PROVENANCE_MATRIX.tsv` 或生成 superseding provenance supplement；
- 对 H1/H2/H3 分别给出 `ACCEPTED / QUARANTINED / SUPERSEDED / UNRESOLVED`；
- 明确哪些旧 C13 raw logs 仍是合法历史证据，哪些结果不能用于科学结论；
- 不静默删除原结果。

成功状态二选一：

- `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`
- `C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_B_READY_FOR_REVIEW`

真正无法在合理工程修复后继续：

`C13_EFFECTIVE_CONFIG_AUDIT_HARD_BLOCKER_WITH_EVIDENCE`

本 Goal 连续运行，不需要用户中途确认。