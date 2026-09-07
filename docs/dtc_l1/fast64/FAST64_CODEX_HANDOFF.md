# DTC FAST64 Codex Goal Handoff

Status: **FAST64.1 ACTIVE_HARD_EXECUTION_FAILURE; R2 RECOVERY PREPARED ONLY**

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

Current execution gate: the historical BICG OO@8192 r1 namespace is
`INVALID_EXECUTION_PATH_CONTAMINATED` after a two-epoch controller anomaly.
The source-backed future remedy is an immutable v2 runner plus explicit
START/TERMINAL attempt receipts; do not advance FAST64.1 or launch R2 until
the current contaminated epoch has naturally terminated and a fresh resource
audit approves memory/swap/output headroom.  See
`handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

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
