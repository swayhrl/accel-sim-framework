# CODEX 109 — C16 E1 Clean Baseline Full Goal V1

## Mode

GOAL MODE / solve-and-continue

This is the complete node109 E1 Goal for this stage.

Do not STOP between clean authority, timing matrix, holdouts, transition diagnostic, and pre-authorized bounded NCU if their gates pass.

Suggested execution branch:

`hrl/c16-e1-clean-baseline-109-v1`

## Read first

Fetch and verify:

`hrl/c16-e1-clean-baseline-handoff-v1`

Read completely:

0. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/FP16_CAST_BRIDGE_CONTRACT_V2.md`

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_clean_baseline_v1/E1_CLEAN_BASELINE_DESIGN_V1.md`
3. this file
4. `docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Latest failed historical recovery authority:

`hrl/c16-e1-qwen25-shape-lowbit-109-v1@5563c7bc9320f6699f351307b2895093d0658d97`

Do not attempt to resurrect the old eight-point RAW input authority again.

## Goal

Create a new clean, durable Qwen2.5-7B authority and finish all currently planned node109 E1 work in one continuous Goal.

Primary matrix:

`{q_proj,down_proj,up_proj} × {M1,M256} × {RAW_BF16,RAW_FP16,AWQ_FP16_INPUT}`

18 total points.

## Stage 1 — new canonical RAW activation authority

Use frozen RAW Qwen2.5-7B:
- revision `a09a35458c702b33eeacc393d103063234e8bc28`
- accepted S2_TEXT token SHA `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

Run one natural Layer0 M2048 prefill replay and live-hook:
- self_attn.q_proj input
- mlp.down_proj input
- mlp.up_proj input

Freeze each M2048 tensor.

Derive:
- M256 = exact first 256 rows
- M1 = exact first row

Persist all tensor hashes and identity metadata.

Then regenerate the same authority in a fresh process.

Require all three M2048 activation SHAs identical.

No historical E1 output SHA is a gate for this new baseline.

## Stage 2 — direct replay qualification

For q_proj/down_proj/up_proj at M1/M256:

- direct RAW_BF16 module replay;
- establish deterministic output contract;
- record output SHA and shape/stride.

Prefer bitwise repeatability.

## Stage 3 — RAW_FP16 bridge + exact same-input AWQ

For every canonical activation:
- cast BF16 -> FP16;
- require finite values;
- audit deterministic BF16 -> FP16 cast under FP16_CAST_BRIDGE_CONTRACT_V2; round-trip bitwise equality is not required.

Construct RAW_FP16 module weights/bias by exact dtype cast only.

Record all weight/bias SHAs.

The exact same FP16 activation bytes must be used by:
- RAW_FP16
- AWQ_FP16_INPUT

If AWQ accepted backend cannot consume this exact FP16 input without backend changes, STOP.

## Stage 4 — run all 18 timing points

For each point:
- 2 warmups
- 7 measured iterations
- CUDA-event timing around exact semantic module call
- preserve raw samples
- deterministic rotated order
- report min/median/max/CV

Record:
- role
- M
- implementation
- input/weight/output dtype
- shape/stride
- module class
- path/kernel fingerprint
- output hash

No model-load time.

## Stage 5 — analyze interaction

Compute:
- RAW_FP16 / RAW_BF16
- AWQ / RAW_FP16
- M256 / M1 within each implementation
- per-role interaction:
  I = log(AWQ/RAW_FP16 at M256) - log(AWQ/RAW_FP16 at M1)

Old historical eight-point values may be shown only as a separately labeled historical table.

Never numerically merge them into the clean baseline.

## Stage 6 — CODE holdout

Search existing local/node164 assets first.

If a durable common Qwen2.5 CODE token authority exists:
- run RAW natural Layer0 replay
- capture canonical down_proj M2048
- derive M1/M256
- run:
  RAW_FP16 M1/M256
  AWQ_FP16_INPUT M1/M256

Same-input contract.

If no common authority exists:
`CODE_HOLDOUT_NOT_RUN_NO_COMMON_AUTHORITY`

Continue.

Do not open a new token-generation campaign.

## Stage 7 — bounded M1023/M1024 transition diagnostic

If the frozen AWQ runtime still proves a deterministic threshold near M=1024:

Run down_proj:
- AWQ M1023
- AWQ M1024
- RAW_FP16 M1023
- RAW_FP16 M1024 if cheap

Use rows from the same canonical M2048 activation.

Record path fingerprint and native timing.

No arbitrary M sweep.

## Stage 8 — conditional NCU, already authorized

Do not STOP for permission.

Entry gate:
1. >=5% material AWQ-vs-RAW_FP16 difference at some M;
2. difference exceeds ordinary timing dispersion;
3. same role shows shape-dependent ratio or the threshold diagnostic shows a path discontinuity;
4. lightweight fingerprint suggests real kernel/path difference.

If PASS:

select role maximizing:

`abs(log(R_awq_M256) - log(R_awq_M1))`

Profile exactly:
- M1 RAW_FP16
- M1 AWQ
- M256 RAW_FP16
- M256 AWQ

for that role.

If transition is dominant, add at most:
- AWQ M1023
- AWQ M1024

Collect only available unit-resolved metrics:
- L1/TEX requested bytes
- L2 requested bytes
- DRAM bytes
- occupancy/active warps if available
- tensor/math/SM utilization if available
- launch geometry/kernel identity

Preserve exact metric names/units.

Normalize traffic by output elements.

If semantic selector cannot be resolved:
`NCU_SELECTOR_UNRESOLVED`

Continue to closure.

Do not launch NVBit/full address trace.

## Stage 9 — optional Llama RAW-only sanity

Only if Llama-3.2-1B is already locally present and direct replay is trivial.

May run one q_proj-like and one MLP projection at M1/M256 as RAW-only shape sanity.

Do not download anything.
Do not block E1 if unavailable.

## Stage 10 — evidence/log/Git closure

Create:

`docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1/`

with all artifacts required by the design.

Update:

`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

Explicitly record:
- old eight-point RAW authority failure;
- new clean authority;
- all new numeric results;
- interpretation;
- superseded conclusions;
- next question;
- stop condition.

Generate SHA256SUMS.

Commit, push, fetch-back/remote verify, clean worktree, release GPU lock, STOP.

## Solve-and-continue

Routine engineering issues:
solve and continue.

Only STOP early for:
- new canonical activation is nondeterministic;
- RAW/AWQ cannot share the exact FP16 activation without changing accepted AWQ backend;
- RAW_FP16 requires more than dtype casting;
- model/token/runtime identity failure;
- genuine GPU/runtime corruption;
- scientific contract change not covered by the design.
