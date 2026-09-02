# CODEX_NEXT_STAGE — Track A

## Status

Accepted:
- M1 PASS
- M2 PASS after M2-RF
- G3-0 PASS
- G3-1 PASS
- G3-2/G3-2B PASS
- G3-2C PASS
- G3-3 PASS

Accepted Core start:

`1b18b3c5da6e5ba22e4a03c20e3adce498311336`

Accepted Framework evidence head before this handoff:

`a3af1f34b4e6fcac4f43faf8d80d8a914eb34958`

## Next authorized target

Resume Codex Goal/target mode and execute as one continuous macro target:

`G3-4A -> G3-4B -> G3-5A -> G3-5B -> G3-CLOSEOUT -> M1_M3_VM_BASELINE_CLOSEOUT`

Full specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_4_G3_5_FINAL_CLOSEOUT.md`

Do not stop for ordinary successful transitions. Continue automatically when each internal gate PASSes.

After final macro closeout, commit/push both repositories and STOP before M4B.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M3_G3_4_G3_5_FINAL_CLOSEOUT.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. G3-2C/G3-3 closeout review evidence
9. accepted M1/M2/G3-1/G3-2 review packs
10. long-lived VM specs and paper parameter ledger

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core:
`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Expected Core start:
`1b18b3c5da6e5ba22e4a03c20e3adce498311336`

Framework:
`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull the latest Framework handoff before implementation.

## G3-4A — page-size foundation

Validate separate run-selected 64KB and 2MB modes.

Generic v0 does not need a simultaneous mixed-page OS/promotion policy. If mixed pages already coexist cleanly, test them; otherwise explicitly document one configured page size per run as `MODELING_DECISION`.

Required exact checks include 64KB/2MB offset, coverage boundary, page-size-aware TLB tags/fills, radix/PWC keys, range separation and M2 64KB regression.

Do not implement 4KB or target-paper sub-entry just to expand scope.

## G3-4B — non-zero TLB lookup timing

Current TLBs have finite ports but functional/zero service latency. Add explicit configurable L1 and L2 lookup service latency.

Generic baseline seed:
- L1 = 10 core cycles
- L2 = 80 core cycles

These are generic/reference-motivated, not target Segmentation-paper exact parameters.

Required semantics:
- port consumed once at lookup launch;
- lookup waits for service completion without re-probing/re-consuming ports;
- hit/miss counted once;
- accepted pending-MSHR retry bypass remains intact;
- new waiter still performs normal first lookup;
- L2 hit fills L1 only when L2 result becomes available;
- no data request before translation READY.

Hard STOP if the old polling/retry pollution pattern reappears.

## G3-5A — latency decomposition

Implement the accounting contract from the stage spec.

Separate requester/waiter timing from unique MSHR/walk timing. Do not multiply shared walk work by waiter count or force overlapping intervals into a fake additive total.

Required analytical expected-vs-actual timing test must cover L1 hit, L2 hit, PTW, PWC/PTE memory and merged waiter behavior.

## G3-5B — causality/sensitivity

Only after correctness gates PASS.

Required minimum sweeps:
- L2 TLB capacity: 3 points around 768;
- translation MSHR: 3 points;
- walkers: 1 / 4 / 16 or justified equivalent;
- PWC: OFF / FINITE-128 / IDEAL;
- M2 fixed-latency vs M3 real-memory PTW;
- 64KB vs 2MB on at least one valid trace;
- zero-latency diagnostic vs non-zero generic TLB timing on a bounded case.

Use structured TSV/CSV and exact provenance. If only LUD and BFS exist, use only those and state that limitation.

Do not tune away non-monotonic results; investigate and explain them with measured resource/timing statistics.

## Parameter evidence rules

Maintain `PARAMETER_EVIDENCE_LEDGER.md`.

Do not blur:
- `SEGMENTATION_PAPER_KNOWN`
- project `MODELING_DECISION`
- `REFERENCE_OTHER_PAPER`
- `DIAGNOSTIC`
- `UNKNOWN`

In particular, target-paper known TLB capacities/walkers do not make the generic 10/80-cycle lookup seed or 128-entry PWC paper-exact.

## Required final artifacts

Complete:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

and create:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

Maintain throughout:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

## Hard STOP conditions

STOP before advancing on any:
- repeated TLB probing/port consumption while a lookup is already in service;
- recursive PTE translation;
- response misassociation or request loss;
- duplicate waiter wakeup/store/atomic side effect;
- hierarchy/PWC/address-range collision or overflow;
- M1/M2 regression;
- deadlock or unexplained nondeterminism;
- inconsistent/negative latency accounting;
- provenance ambiguity;
- need for a materially new architecture decision not covered by the final-stage spec.

## Final STOP

After M3 PASS and `M1_M3_VM_BASELINE_CLOSEOUT`:
- push Core + Framework;
- report final SHAs;
- STOP.

Do NOT start:
- M4B
- Segmentation
- L2-TLB sub-entry/coalescing
- synthetic KV
- page fault/migration/UVM/MCM
- new AI-aware VM mechanisms.