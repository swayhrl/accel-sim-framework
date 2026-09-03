# DTC-L1 Current State

Last coordination update: 2026-09-03

Status: **M1/M2/M3 PASS; M4 BLOCKED ON SOURCE-REACHABLE COMPLETION ACCOUNTING; RECOVERY AUTHORIZED**

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

M0 branches remain read-only design anchors.

## Closed stages

### M1 — PASS

Review pack: `docs/dtc_l1/review_packs/M1_FOUNDATION/`.

Validated M1 Core anchor: `48b0be73833fc89fcf833349e82886ddc6d883b0`.

M1 established LEGACY neutrality, Paper-Base PIB/Tag/MSHR/lower-cap behavior, common counters/parser infrastructure, and B01-B09 HARD validation.

### M2 — PASS

Review pack: `docs/dtc_l1/review_packs/M2_IO_READ/`.

Validated scope includes dedicated Paper-IO whole-line request/response/PIB-writeback lifecycle, no traditional L1D MSHR capacity/merge dependence, physical `{id,generation}` identity, partial allocation/no rollback, lower caps/issue width, I01-I15, high-MLP no-MSHR proof, and closed counters/invariants.

### M3 — PASS

Review pack: `docs/dtc_l1/review_packs/M3_OO_SECTOR/`.

Validated M3 scope includes whole-line OO random-access PIB, deterministic ready retirement, line-level Ref Count and Shadow Ref, pending-hit merge/wakeup, active reclamation, O01-O13, IO-vs-OO causal HOL, and 4x32B sector extension S01-S09. Real modes 2/3/4 VecAdd diagnostic self-checks passed.

Do not redo or weaken M1-M3 unless the active M4 recovery proves a real regression.

## M4 partial progress before current stop

M4 source semantics audit:

`docs/dtc_l1/implementation/M4_MEMORY_OP_SEMANTICS.md`

Partial work already preserves/observes current Store, Atomic, and architectural-bypass lifecycle semantics without changing their source request/cache/ack/side-effect routes. Atomic read-merge prohibition remains mandatory.

The frozen PTX frontend proxy-fence reachability limitation remains established and is governed by:

`docs/dtc_l1/goal/M4_FENCE_REACHABILITY_RESOLUTION.md`

No PTX fence frontend support or `membar -> FENCE_OP` substitution is authorized.

## Active M4 HARD failure — completion accounting

Failure evidence:

`docs/dtc_l1/implementation/M4_COMPUTE_BRINGUP_FAILURE.md`

Failure checkpoints:

- Core: `56a9230e4a538b69a30673ebdf66c42526fb324a`;
- Framework: `5f674edccdf48dc768155fbd008723dc8a126b31`.

The first provenance-controlled PolyBench 2DConv triplet exposed:

- `PAPER_IO`: `dtc_l1_io_complete_instruction` aborts on `pending >= dependencies`;
- `PAPER_OO`: `dtc_l1_oo_complete_instruction` aborts on the same invariant;
- `PAPER_BASE`: 240-second wall-clock `TIMEOUT_DIAGNOSTIC`, not yet classified as deadlock.

IO and OO use different retirement policies but share the failing bridge between DTC-owned 128B line dependencies and GPGPU-Sim `m_pending_writes` / scoreboard completion state. Therefore the active issue is a common completion-accounting/ownership integration bug, not currently evidence of a Tag->Physical, Ref Count, Merge, or sector-state mechanism failure.

Current source already registers DTC cacheable-load pending writes using unique coalesced 128B line references in `ldst_unit::issue()`, and IO/OO PIBs retain unique 128B line references. The failure means the registered/remaining aggregate and retirement-owned dependency count are not conserved for at least one real workload instruction. Root cause is not yet frozen.

## Authorized recovery

Primary active specification:

`docs/dtc_l1/goal/M4_COMPLETION_ACCOUNTING_RECOVERY.md`

Required order:

1. reproduce/localize the first failing UID/PC and exact cardinality values;
2. add a per-instruction DTC dependency ownership ledger/checker;
3. trace all relevant `m_pending_writes` mutations and classify root cause as premature consumption, cardinality divergence, duplicate completion, cross-instruction aggregate alias, or another source-proven category;
4. apply only the minimal source-backed repair;
5. add permanent cardinality/exactly-once regressions;
6. rerun the exact 2DConv PAPER_IO/PAPER_OO cases to full completion/accounting closure;
7. rerun the closed-stage regression subset because the fix touches shared load-completion glue;
8. separately classify PAPER_BASE timeout from progress evidence;
9. only after recovery PASS, resume the remaining M4 source-reachability/fence, Store/Atomic/bypass/mixed/workload/parser/CSV closeout automatically.

No new human authorization is required after full recovery PASS.

## Recovery prohibitions

Do not:

- remove/weaken/clamp the failing accounting assertion;
- force `m_pending_writes` to zero;
- release scoreboard registers without exact ownership closure;
- change frozen 128B DTC dependency granularity merely to match the observed failing value;
- reintroduce conventional L1D MSHR/fill as the DTC read backend;
- change L2/NoC/DRAM;
- implement PTX fence frontend semantics;
- begin M5.

## Final boundary

M4 remains unaccepted until this source-reachable correctness failure is closed and all remaining active M4 HARD gates pass. Only then may `LATEST_REPORT.md` become `READY_FOR_M5_REVIEW`.

M5 remains forbidden.
