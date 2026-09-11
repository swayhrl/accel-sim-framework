# C13 effective-config audit — unattended execution addendum

状态：`AUTHORIZED_UNATTENDED_CONTINUATION`

本 addendum 仅改变调度与无人值守推进方式，不改变 `C13_EFFECTIVE_CONFIG_AUDIT_GOAL.md`、Path A/Path B 的科学验收条件。

## 0. 目的

用户将暂时离开约 7 小时。目标是在不牺牲证据质量的前提下，避免 full-ROI control/replay 串行等待导致机器和 Codex 空转。

当前 root cause 已明确指向 C13 config synthesis：MANUAL override 继承 source profile 的 `gpgpu_vm_l2_tlb_mode=1`，而 intended exact-page diagnostics 需要显式 `mode=0`。因此所有 repaired exact-mode arms 必须通过 effective-config fail-fast gate。

## 1. 推测性并行原则

验收依赖仍保持：EQ1 -> EQ2 -> repaired scientific matrix promotion。

但**执行调度不必严格串行**。

在完成静态 config synthesis 修复和 launch-before effective receipt 后，只要资源满足 adaptive admission，可同时启动独立 controls / repaired arms，并将尚未通过 equivalence gate 的科学 arms 标记为：

`SPECULATIVE_REPAIRED_EXECUTION_PENDING_EQ_GATE`

这些 arm 的 raw logs 可以完整跑完并保存，但在 EQ1/EQ2 正式通过前不得晋升为 accepted scientific evidence。

如果 equivalence gate 失败：

- 不覆盖 speculative raw logs；
- 将受 gate 影响的结果标记 `QUARANTINED_BY_EQUIVALENCE_GATE_FAILURE`；
- 自动转入 Path B 根因审计；
- 不把 speculative 性能趋势用于科学结论。

## 2. Control 调度

静态 audit 完成后，若资源 GREEN，允许 EQ1 与 EQ2 **同时执行**：

- `C13-EQ-P320S10-C12BIN-EXACTMODE`
- `C13-EQ-P320S10-NEWBIN-EXACTMODE`

正式验收逻辑仍然先判 EQ1：

1. EQ1 必须复现 canonical C12 Prefill F7-L10；
2. 只有 EQ1 通过后，EQ2 才能用于证明 new binary default-off equivalence；
3. 若 EQ1 失败，EQ2 即使数值接近也只能保留为 diagnostic evidence，自动转 Path B。

这样允许在 wall-clock 上重叠两个 full-ROI Prefill control，而不放松因果/验收顺序。

## 3. Repaired scientific arms 的推测性提前执行

当且仅当以下静态条件全部通过后，可在 EQ controls 尚在运行时提前执行 repaired scientific arms：

- config synthesis 已显式覆盖 `-gpgpu_vm_l2_tlb_mode 0`；
- independent option folding 显示 intended mode/entries/assoc/sets/Segment/Lseg；
- command receipt/config SHA/binary SHA/Core HEAD/trace SHA/registration SHA 全部固定；
- output dir 为 fresh `*-REPAIRED-EXACTMODE-A1`；
- launcher preflight 会在 effective mode != intended 时 fail-fast。

允许提前准备/执行：

### H3 repaired

- Prefill P8
- Prefill P9
- Decode D11

### H2 repaired

- Prefill P320 no Segment, exact mode
- Prefill P768 + Segment N8/L10, exact mode

### H1 repaired

- Prefill same-new-binary exact320 control
- Prefill selective candidate
- Decode same-new-binary exact320 control
- Decode selective candidate

若 EQ2 与 Prefill H1 control 完全相同，可复用同一 run，但 provenance 必须明确一份 raw log 同时承担 EQ2 与 H1-control 两个角色，不得复制/伪造第二份运行。

## 4. 并发管理

沿用 C13 adaptive admission，不因用户无人值守而突破资源安全线。

优先级：

1. EQ1 / EQ2
2. Decode repaired arm（通常较短）
3. Prefill H3/H2
4. H1 candidate/control

根据实时 CPU idle、MemAvailable、PSI、iowait、swap-in/out 逐步扩容。

- 资源 YELLOW：保持已有健康 worker，不新增；
- 资源 RED：暂停新 admission，不主动杀健康 arm；
- OOM/resource-kill：隔离 failed attempt，降低并发，fresh dir 重试；
- 禁止干预其他项目/用户进程。

此前用户已授权在充足 CPU/内存条件下扩大并发；但本阶段仍应由实时 adaptive gate 决定，而非固定追求最大 worker 数。

## 5. 每个 arm 完成后的自动动作

每个 arm terminal 后立即：

1. raw-log SHA / config SHA / command receipt recheck；
2. effective geometry receipt 与 intended row 一致性；
3. terminal marker / telemetry / PTE / object conservation；
4. per-kernel cycle closure；
5. cumulative vm_* closure；
6. 记录状态：`PASS_PENDING_EQ_GATE` / `ACCEPTED_AFTER_EQ_GATE` / `QUARANTINED`。

不要等全部 replay 结束后再统一发现 geometry 错误。

## 6. EQ gate 结束后的自动 promotion

### EQ1 + EQ2 都 PASS

- 将所有 geometry/provenance 正确且 terminal PASS 的 repaired speculative arms promotion 为正式 repaired evidence；
- 重新生成 H1/H2/H3 tables；
- old wrong-mode rows 继续保留并标 `SUPERSEDED_WRONG_L2_MODE_SUBENTRY16`；
- 不把旧 mode=1 结果混入 repaired scientific comparisons。

### EQ1 或 EQ2 FAIL

- 自动转入 Path B；
- 不等待用户确认；
- 先完成 source/config correctness 根因审计；
- 仅在修复后重新生成最小必要 controls/replays。

## 7. 如果 replay 提前结束，继续做的离线任务

若用户返回前 repaired matrix 已全部 terminal，不要停止 Goal。继续完成以下只读工作：

### U1 — superseding C13 analysis

重新生成：

- fine-latency sweep 与新的 measured crossover bracket；
- corrected capacity 2x2 factorial；
- repaired selective candidate-control；
- kernel691 / operator / layer attribution；
- wrong-mode old run vs repaired exact-mode 的 engineering-only impact audit。

旧 mode=1 运行只能用于解释 config bug 的工程影响，不能被重新包装成 Sub-entry scientific result。

### U2 — cross-layer postmortem

对 repaired H2/H3 重点回答：

- exact320 与 Segment 各自 effect 以及 interaction 是否仍存在；
- Prefill 传统 walks/PTE-DRAM 的变化真正来自什么组合；
- kernel691 在 corrected exact geometry 下是否仍是热点；
- Lseg 8/9/11 的符号结论是否保留。

### U3 — next-stage decision memo（只写文档，不启动新实验）

生成：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C13_EFFECTIVE_CONFIG_AUDIT/NEXT_STAGE_DECISION.md`

至少给出：

1. repaired C13 后最强 3–5 条 measured facts；
2. 被旧 wrong-mode C13 推翻/修正的结论；
3. object-selective policy 是否仍值得；
4. Segment × exact-TLB interaction 是否值得作为主研究问题；
5. 下一阶段最多 3 个最小实验建议；
6. 哪些方向建议停止投入（例如 Sub-entry，如果证据仍然弱）；
7. 每个建议实验的 hypothesis / minimal matrix / acceptance / estimated runtime。

**不得自动启动 NEXT_STAGE_DECISION 中的新实验。** 用户回来后由 ChatGPT/用户审定。

## 8. Git / evidence discipline

- 禁止 `git add .` / `git add -A`；
- raw logs 不提交；
- old invalid raw logs 不删除；
- repaired raw logs 使用 fresh dirs；
- audit/review pack/轻量 TSV/脚本可提交；
- 每个阶段至少形成 checkpoint commit，避免长时间无人值守后只有本地状态。

## 9. 无人值守最终状态

优先目标：

`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_A_READY_FOR_REVIEW`

若转 Path B：

`C13_EFFECTIVE_CONFIG_AUDIT_CLOSED_PATH_B_READY_FOR_REVIEW`

如果 replay 尚未全部结束但进展健康，可保持：

`C13_EFFECTIVE_CONFIG_AUDIT_REPAIRED_REPLAYS_IN_PROGRESS`

并提交 checkpoint / handoff，明确 active arms、completed arms、resource state 与下一自动步骤。
