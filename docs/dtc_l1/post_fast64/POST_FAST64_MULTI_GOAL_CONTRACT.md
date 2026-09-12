# POST-FAST64 Multi-Goal Execution Contract

Status: **ACTIVE PLANNING AUTHORITY — POST-FAST64 ONLY**

## 0. Frozen authority and non-regression boundary

The completed FAST64 result is immutable scientific authority:

- Framework branch: `hrl/decoupled-l1-fast64-v0`
- Framework commit: `18a68dcccd795f1b6cda75504e9450d00c9cee02`
- terminal state: `FAST64_COMPLETE_READY_FOR_REVIEW`
- final review pack: `docs/dtc_l1/fast64/review_packs/FAST64_FINAL/`

No post-FAST64 task may rewrite, demote, relabel, replace, or silently reinterpret an accepted FAST64.0-.7 result. New simulation evidence is always:

`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`

unless a later researcher-approved program explicitly defines a new formal result set. Post-FAST64 work must never enter the accepted FAST12 GM or overwrite FAST64 compact evidence.

The coordination branch is:

`hrl/decoupled-l1-fast64-post-analysis-v0`

All lane branches/worktrees must descend from the frozen FAST64 commit plus this planning authority. Separate lane branches are preferred over multiple Codex windows writing the same branch.

## 1. What the currently launched Goal covers

The existing Goal prompt already covers all four planned workflows, not only one:

- **Lane A — paper-grade result analysis:** prompt P1.
- **Lane C — quantify no-MSHR duplicate requests:** prompt P2.
- **Lane B — physical-pool non-monotonicity/root cause:** prompt P3, then part of P5/P6.
- **Lane D — observer-only telemetry and diagnostic reruns:** prompt P4/P5.
- **Integration:** prompt P6.

The current window may continue as an orchestrator and may execute any lane it already owns. New windows must use distinct lane branches and avoid duplicating live work.

## 2. Persistent post-FAST64 state machine

Logical review progression is:

`POST0_AUTHORITY_FREEZE`
`-> A_PAPER_RESULTS_READY`
`-> B_PHYSICAL_CAUSAL_READY`
`-> C_DUPLICATE_MISS_READY`
`-> D_OBSERVER_EVIDENCE_READY_IF_NEEDED`
`-> E_INTEGRATED_ANALYSIS_READY`
`-> POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW`

Lanes A/B/C/D may execute physically in parallel. Their PASS states are independent until integration E. A lane gate blocks promotion of that lane, not useful work in other lanes.

## 3. Evidence classes

Every artifact must declare one of:

- `ACCEPTED_FAST64_EVIDENCE` — byte-identical or hash-bound input from completed FAST64.
- `EXISTING_DATA_DERIVED_ANALYSIS` — arithmetic/reformatting/normalization from accepted evidence only.
- `NEW_DIAGNOSTIC_TELEMETRY` — counters or traces added only for observation; not a primary result.
- `POST_FAST64_EXPLORATORY_RUN` — new simulator execution using diagnostic instrumentation/configuration.
- `SOURCE_PROVEN` — claim directly established by inspected source semantics.
- `MEASURED_CORRELATION` — association observed in data; not causal proof.
- `INSUFFICIENT` — evidence does not support the claim.

Never promote `MEASURED_CORRELATION` to `SOURCE_PROVEN` by prose.

## 4. Mandatory problem-solving behavior

This is Goal mode. Ordinary problems are work to solve, not reasons to stop.

For build/parser/path/controller/resource/row-local/source-observer problems use:

`OBSERVE -> REPRODUCE -> CLASSIFY -> INSPECT SOURCE/EVIDENCE -> TRY SOURCE-CORRECT FIX -> REGRESS -> INVALIDATE ONLY AFFECTED EXPLORATORY DATA -> RESUME`

Codex must attempt reasonable source-correct alternatives before asking the researcher.

Do **not** stop merely for:

- one failed diagnostic row;
- parser/schema mismatch;
- missing optional metric;
- stale path/manifest/controller;
- resource scheduling/admission delay;
- a rejected hypothesis;
- negative/non-monotonic data;
- a telemetry counter proving uninformative;
- a workload-specific issue that can be repaired without changing mechanism meaning.

Pause only when continuing would require one of:

1. changing accepted DTC mechanism semantics;
2. changing accepted FAST64 membership/result identity;
3. inventing a meaning-changing proxy for an unavailable metric;
4. choosing between genuinely irreconcilable scientific interpretations after source inspection;
5. deleting unique accepted evidence;
6. unavailable hardware/storage/credentials with no source-correct alternative;
7. researcher review of a completed scientific conclusion.

A lane waiting on simulation resources is not `GOAL_BLOCKED`; continue source audit, extraction, validators, plot data, and documentation.

## 5. Multi-window ownership and Git discipline

Recommended independent Framework branches:

- Lane A: `hrl/post-fast64-paper-v0`
- Lane B: `hrl/post-fast64-physical-causal-v0`
- Lane C: `hrl/post-fast64-duplicate-miss-v0`
- Lane D orchestration: `hrl/post-fast64-observer-v0`

Recommended diagnostic Core branches when needed:

- non-2D observer Core rooted at accepted Core95: `hrl/dtc-l1-post-fast64-observer95-v0`
- 2D observer Core rooted at accepted Core658: `hrl/dtc-l1-post-fast64-observer658-v0`

Rules:

- one Codex window owns one lane branch/worktree;
- do not let two windows push the same branch concurrently;
- do not edit live runner/controller bytes in place; create versioned future-only files;
- do not modify the frozen FAST64 branch;
- never `git add .` or `git add -A`;
- no raw multi-GB outputs in Git;
- commit/push meaningful scientific checkpoints, not polling/timestamps;
- coordinator integrates compact lane commits only after lane acceptance checks.

## 6. Resource policy

Use fresh measured admission. CPU count alone is not the gate. Check CPU/cgroup quota, distinct physical cores, RSS p95/max, MemAvailable, cgroup memory headroom, active swap-out, memory PSI/OOM, I/O, and output space.

Researcher-authorized disk floor remains: projected post-wave free space >= **10 GiB**. Do not reject merely because filesystem usage shows 99% when projected free space remains above the floor.

Do not delete accepted FAST64 evidence to make space.

## 7. Common validation requirements for any new telemetry run

Every retained exploratory simulator row must record:

- exact parent Core SHA and diagnostic Core SHA;
- diagnostic runtime SHA-256;
- Framework execution identity;
- config SHA-256 and explicit diff from the accepted reference configuration;
- workload/payload identity;
- immutable runner and fresh namespace/UUID;
- natural terminal status;
- strict existing lifecycle/accounting/drain checks;
- observer counters and their source semantics;
- explicit `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT` classification.

Observer qualification requires exact equivalence of pre-existing scientific outputs on cheap controls. At minimum compare cycles, instructions, existing scientific counters, lower/dependency conservation, and terminal drain. Any difference is an observer correctness problem until source-classified.

## 8. Integration acceptance

The post-FAST64 program is ready for review only when:

- Lane A has paper-grade plot-ready tables/figures and per-workload explanations with provenance;
- Lane B classifies every physical-pool hypothesis as `SOURCE_PROVEN`, `MEASURED_CORRELATION`, `NOT_SUPPORTED`, or `INSUFFICIENT` and explains the non-monotonic trend without inventing causality;
- Lane C quantitatively adjudicates the dissertation 4.2.2 duplicate-request claim on accepted FAST12 IO evidence and, if needed, diagnostic OO evidence;
- Lane D, if invoked, proves observer-only equivalence before using diagnostic results;
- integrated analysis states which arrows in `physical pool -> concurrency -> L2 pressure -> pending lifetime -> tag eviction -> duplicate traffic -> performance` are actually supported;
- no new result is mixed into FAST64 GM or presented as dissertation-exact reproduction;
- limitations and unresolved questions are explicit.
