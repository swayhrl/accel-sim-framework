# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1/M2/M3 PASS; M4 RESUMED UNDER VERIFIED SOURCE-REACHABILITY BOUNDARY**

## Source anchors

Frozen M0 framework anchor:

- official: `accel-sim/accel-sim-framework:dev`;
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`;
- M0 branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`.

Frozen M0 core anchor:

- official: `accel-sim/gpgpu-sim_distribution:dev`;
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`;
- M0 branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`.

Active goal branches:

- Core: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`;
- Framework: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`.

M0 branches are read-only design anchors.

## Closed stages

### M1 — PASS

Review pack: `docs/dtc_l1/review_packs/M1_FOUNDATION/`.

Validated M1 Core anchor: `48b0be73833fc89fcf833349e82886ddc6d883b0`.

M1 established exact LEGACY neutrality, Paper-Base PIB/Tag/MSHR/lower-cap behavior, counters/parser infrastructure, and B01-B09 HARD validation.

### M2 — PASS

Paper IO now has a dedicated DTC-owned whole-line read request/response/PIB-writeback lifecycle. The conventional-fill failure and recovery are preserved in the implementation evidence. M2 includes physical `{id,generation}`, no-traditional-L1-MSHR read semantics, partial allocation/no rollback, lower issue/outstanding limits, IO FIFO retirement/HOL, and required directed/resource validation.

### M3 — PASS

Core M3 checkpoint: `90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`.

Framework M3 implementation/parser checkpoint: `800fc95fe2b502e30e76ce1cb6de050f6069178e`.

Validated M3 scope includes:

- PAPER_OO whole-line random-access PIB and deterministic ready retirement;
- line-level Ref Count and Shadow Ref validation;
- pending-hit merge/wakeup;
- active reclamation;
- O01-O13;
- IO-vs-OO causal HOL;
- 4x32B sector extension S01-S09;
- real modes 2/3/4 VecAdd diagnostic self-checks and strict provenance parsing.

Do not redo M1-M3 unless M4 reveals an actual regression.

## M4 current implementation checkpoint

Core checkpoint before the latest specification refinement:

`5aea1cbb41575e31c0c61f97dfc6d77cc15a3c9f`

Framework fence-evidence checkpoint:

`b18eca499b6fe92569070c4ebebe8d7374f6f68a`

M4 source audit/evidence:

`docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`

Partial validated M4 work already includes source-preserving Store/Atomic/architectural-bypass lifecycle observation, modes 2/3/4 VecAdd Store closure, and an available atomic-contention workload with Atomic closure. No M4 PASS is implied yet.

## Verified PTX proxy-fence reachability limitation

Repeated source audit established that the frozen current PTX frontend cannot generate the existing dynamic `FENCE_OP` / async proxy-fence path:

- no `fence` lexer rule;
- no parser token/production/mapping;
- no static PTX decode case;
- no PTX-originating producer of `set_proxy_fence()` / `set_fence_proxy_kind()`;
- PTX `membar` is a distinct `MEMBAR_OP` and cannot be substituted;
- regular dynamic fence behavior is explicitly unsupported.

This is a verified source-domain limitation, not a DTC Tag/PIB/Ref correctness ambiguity.

The old end-to-end PTX F01-F03 requirements were planning-time project tests. Implementing a new PTX fence frontend is unrelated to the Chapter-4 DTC mechanism reproduction and would expand scope unnecessarily.

Authorized disposition:

`docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`

For the frozen source:

- F00A-F00D are the active HARD fence/source-domain gates;
- F01-F03 are `SOURCE_UNREACHABLE_NA` after F00A-F00D close;
- no `membar` substitution or new fence parser semantics may be added;
- accepted workload triplets must have identical source-reachable `FENCE_OP` counts, expected zero;
- discovery of a real source-backed FENCE_OP producer requires STOP and reopens end-to-end fence validation.

This changes the validation boundary only; it does not alter frozen M0 DTC architecture choices.

## Current M4 execution authority

Resume M4 rather than remaining blocked.

Primary files:

- `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`;
- `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`;
- `docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`;
- updated `docs/dtc_l1/goal/VALIDATION_ACCEPTANCE_MATRIX.md`;
- `docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`.

Immediate required work:

1. close F00A-F00D and record F01-F03 `SOURCE_UNREACHABLE_NA`;
2. close W01-W04, A01-A04, BP01-BP02, and refined source-reachable MIX01;
3. finalize `implementation/WORKLOAD_MANIFEST.md`;
4. run at least five provenance-resolved representative Chapter-4 compute workloads under PAPER_BASE/PAPER_IO/PAPER_OO;
5. require matching dynamic instruction/Load/Store/Atomic/source-reachable-FENCE_OP counts and closed invariants/provenance/accounting;
6. generate/validate required compact CSV/parser outputs;
7. create `review_packs/M4_COMPUTE_BRINGUP/` only after all active M4 HARD gates pass;
8. update `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP.

## Final scope boundary

M5 remains forbidden. No final thesis speedup reproduction, equal-area study, graphics proxy study, or final figure generation is authorized before independent M4 review.
