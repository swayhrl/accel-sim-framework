# C16 Next-Lineage Campaign Framework V11 — Scope

## Purpose

Use the completed Qwen2.5-7B raw/AWQ V5–V10 campaign as the golden fixture to convert one-off scripts and learned failure modes into a reusable, resumable, fail-closed campaign framework for the next model lineage.

This task runs in parallel with 174-new V11 analysis. It MUST NOT start a Qwen3 formal GPU campaign before 174-new produces an explicit execution authorization/contract.

## Base authority

- Qwen2.5 pair-closure producer HEAD: `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`
- Qwen3 static planning authority: `cd74256d698d9949d222703db8bb077a3581792a`
- Qwen3 exact model/revision: `Qwen/Qwen3-8B` @ `b968826d9c46dd6066d109eabc6255188de91218`
- Qwen3 planning contract requires exact layer weights, exact incoming hidden state, position/attention state, layer-local KV state, runtime deployment identity, output equivalence, kernel-signature equivalence, and full-function global-address-path audit before formal capture.

## Hard guardrails

- `FORMAL_ADMISSION_CONCURRENCY = 1` remains immutable.
- No Qwen3 formal trace or catalog admission in this task.
- No mutation of accepted Qwen2.5 raw/catalog.
- No historical/prospective input rewrite.
- No cross-process absolute-VA comparison.
- No cross-shard chronology/reuse-distance reconstruction.
- No static-set reuse across different kernel implementations; derive fresh SASS sets for every qualified target implementation.
- No launch-order semantic inference.
- No hard-coded PASS rows: every gate result must be produced by executable validation.
- No unbounded debugging loops. Each stage gets bounded fallback methods and then emits `BLOCKED.json` and stops safely.

## Desired outcome

A single next-lineage campaign driver should be able to run unattended for hours, stage-by-stage, with deterministic receipts and restart points. A new model should mainly require an adapter/config plus an explicit scientific target policy, not another sequence of ad-hoc versioned scripts.
