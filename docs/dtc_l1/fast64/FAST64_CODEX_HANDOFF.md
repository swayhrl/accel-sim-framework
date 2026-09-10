# DTC FAST64 Codex Goal Handoff

Status: **GOAL ACTIVE; FAST64_1_PLATFORM_PASS; FAST64.2 REPAIR_QUALIFICATION_ACTIVE; FAST64.2 COUPLED-STRESS STRICT-NEGATIVE PRESSURE ABSENT; FAST64.3 HAS DWT2D/GEMM/ATAX BASE STRICT-VALID PRECOMPUTES PENDING FAST64.2 ACCEPTANCE**

Framework branch:

`hrl/decoupled-l1-fast64-v0`

Core authority is deliberately split:

- `MECHANISM_BEHAVIOR_ANCHOR`:
  `hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.
- `FAST64_FORMAL_INSTRUMENTED_CORE`:
  `hrl/decoupled-l1-m5-v0@bbcbb5e7565417102087bc80b14c349b4e568c05`.

The latter changes no DTC mechanism behavior: it exposes the pre-existing OO
`DTC_L1_lower_cap_full_events` counter and passed exact NN Base/IO/OO
differential. Formal FAST64 execution uses the instrumented Core/runtime; the
former remains the mechanism semantic/source anchor.

All formal FAST64 acquisition, including later dynamic-pool rows, records the
frozen execution-scientific Framework snapshot
`037f008b330eb230353b60edf126d6be9f45afdc`.  The current worktree HEAD is a
controller/review identity and must not be substituted for that execution
source in a result manifest.

FAST64.1 is now PASS. Both historical BICG OO r1 namespaces (8192 and high
cap) remain `INVALID_EXECUTION_PATH_CONTAMINATED`; all historical r1 is
superseded/nonformal. The source-backed remedy, the complete seven-row
immutable-v2 R2 qualification wave with explicit START/TERMINAL receipts,
naturally terminated and strict-validates through the versioned alias-v2
reader. BICG IO, BICG OO, and GESUMMV IO candidate/high comparisons are exact
matches, and every required candidate cap 8192 records
`DTC_L1_lower_cap_full_events = 0`. The frozen closeout dependency bytes
remain unchanged and fail-close only because their reader counts the normal
`perf_counter.csv.gz` symlink as a second stream; see the alias-v2 compact
evidence/manifest at `generated/qualification_r2_full_wave_alias_v2/`.
Future work must continue to use separate versioned files. Old r1 jobs remain
diagnostic and are not a scientific launch barrier. See
`handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md` and
`handoffs/FAST64_1_R2_CLOSEOUT_DEPENDENCY_FREEZE.md`.

### Live trace-counter interpretation

Do not diagnose a live first-kernel trace row as stalled solely because its
`gpu_tot_sim_insn` or `gpu_tot_issued_cta` perf fields are zero.  Source
`src/gpgpu-sim/gpu-sim.cc` registers both completed-grid fields alongside the
current-grid `gpu_sim_insn` and `gpu_sim_cycle` fields; `update_stats()` moves
the latter into the former only at kernel completion.  The live GESUMMV R2
IO@8192, IO@1048576, and pending Base rows currently have respectively about
36.0M, 33.8M, and 8.18M `gpu_sim_insn`, despite zero completed-grid totals.
Their advancing current-grid instruction/cycle counters are the applicable
simulator-level progress evidence until natural terminal accounting occurs.

The unsatisfied FAST64.1 HARD requirements block only FAST64.1 result/stage
promotion.  They do not block the persistent Goal.  The remote host-policy
review supersedes the former `74-80` exclusive-pool wait: CPU placement is not
a formal row identity.  Prefer a naturally free historical CPU when available,
but otherwise use topology-aware candidates that are not singleton/narrow
pinned by a live simulator; broad `0-511` affinity is soft contention only.
R2 remains taskset-pinned and no existing process affinity may be modified.

Use `util/dtc_l1/audit_fast64_r2_resources.sh --output <external-tsv>` for the
read-only 60-second `FAST64_R2_RESOURCE_AUDIT_V1`.  It makes the autonomous,
conservative N_safe decision from CPU/cpuset/topology, observed p95 RSS and
historical R1 output, cgroup headroom, swap/OOM/PSI/I/O deltas and output
space.  `safe_to_launch=YES` is an ordinary operational admission decision,
not a researcher approval; the audit itself cannot launch a process.

FAST64.2's former high-cap/create-queue requirement is resolved by researcher
authority: retain the completed BICG/IO high-cap run only as
`FAST64_2_HIGH_CAP_NEGATIVE_CONTROL`, and acquire a separate diagnostic-only,
binding-lower-cap/source-coupled-candidate positive stress.  It changes no
Core semantics and remains outside all performance aggregates.  The exact
source proof, fixed NN/IO `cap=512, PIB=1` construction, and later acceptance
conditions are in `handoffs/FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.

## Mission

Carry FAST64 continuously from FAST64.0 through FAST64.7 and stop only at:

`FAST64_COMPLETE_READY_FOR_REVIEW`

The primary goal is to produce a rigorous, efficient simulator evaluation of
Base/IO/OO Decoupled-Tag Cache using the frozen FAST64 platform and FAST12
payload roster while preserving existing M5 mechanism-fidelity/heavy evidence.

## Mandatory reading order

At Goal start and after every interrupted resume, read:

1. `FAST64_RESEARCH_SCOPE.md`
2. `FAST64_PLATFORM_CONTRACT.md`
3. `FAST64_WORKLOAD_MANIFEST.tsv`
4. `FAST64_EXPERIMENT_MATRIX.md`
5. `FAST64_ACCEPTANCE_CONTRACT.md`
6. `FAST64_RESULT_IDENTITY.md`
7. `FAST64_HEAVY_EVIDENCE_BOUNDARY.md`
8. `FAST64_STAGE_HANDOFF_SCHEMA.md`
9. `FAST64_EXECUTION_RUNBOOK.md`
10. existing FAST64 handoffs, if any

Also read only the minimum historical M5/C2P documents needed to verify a
specific reused fact. Do not let historical stale state override the FAST64
contracts.

## Non-negotiable execution behavior

### Solve problems instead of stopping

For ordinary technical failures, do not return control to the researcher after
one failed attempt.

Use the issue loop:

`OBSERVE -> REPRODUCE -> CLASSIFY -> INVESTIGATE SOURCE/TRACE/CONFIG ->
REPAIR/RECONSTRUCT -> REGRESS -> INVALIDATE AFFECTED RESULTS -> RESUME`

Try reasonable source-correct alternatives until the issue is solved or a
true researcher-decision boundary is reached.

Ordinary issues include dependency/build/config/trace/parser/storage-path/
worker scheduling/output-checker/runtime inefficiency/workload-local assertion
or counter defects.

A negative speedup is not a failure.

### Protect scientific meaning

Do not:

- modify DTC mechanism semantics to improve results;
- change FAST12 membership or input after seeing IO/OO performance;
- import C2P cache-search behavior into DTC;
- use C2P's 64-KiB/32-way L1 as FAST64 Base;
- mix observer identities within a triplet;
- treat a diagnostic stress run as a performance result;
- truncate formal rows with max-cycle cutoff to save time;
- delete unique scientific artifacts without an explicit retention proof.

### Preserve useful parallelism

Logical stage order controls acceptance, not all physical data acquisition.
Within the active stage, run independent eligible work concurrently under a
measured dynamic `N_safe` worker pool.

Do not serialize workload-by-workload when rows are independent.

## Stage transition rule

For every stage:

1. execute the required work;
2. resolve ordinary issues;
3. verify every HARD item in `FAST64_ACCEPTANCE_CONTRACT.md`;
4. write the exact stage handoff required by `FAST64_STAGE_HANDOFF_SCHEMA.md`;
5. update compact result registry/evidence;
6. `git diff --check`;
7. explicitly stage only intended files;
8. commit/push the Framework branch;
9. reread the runbook and next-stage gate;
10. continue automatically.

Do not pause merely to ask permission for a normal stage transition.

## Git discipline

- Never use `git add .` or `git add -A`.
- Preserve pre-existing untracked artifacts.
- Do not commit raw large traces/logs.
- Commit hashes/manifests/summaries/raw-log indices.
- Do not modify the Core branch unless a generic source-correct defect is
  demonstrated and the change is required to continue.
- If Core must change, run required regressions and explicitly invalidate all
  affected FAST64 result identities before resuming.

## Researcher-decision boundary

Pause only if continuation requires:

- changing DTC architectural semantics;
- changing FAST12 membership/input after performance observation;
- materially redefining FAST64's frozen platform;
- accepting a proxy that changes the research question;
- choosing between irreconcilable scientific/source interpretations;
- deleting unique evidence without a safe retained copy;
- unavailable credentials/hardware/storage with no source-correct alternative;
- final review after the terminal state.

Everything else should be investigated and solved within the Goal.

## Required terminal report

At `FAST64_COMPLETE_READY_FOR_REVIEW`, report:

- final Framework/Core SHAs;
- FAST12 Base/IO/OO performance and GM-FAST12;
- structural-pressure and live-miss findings;
- IO-vs-OO causal explanation;
- sensitivity findings;
- all negative/weak cases and classifications;
- Tier A mechanism-fidelity evidence used;
- Tier C heavy auxiliary evidence retained;
- differences/limitations versus the dissertation platform;
- review-pack paths and raw-log index;
- any optional background work still running.
