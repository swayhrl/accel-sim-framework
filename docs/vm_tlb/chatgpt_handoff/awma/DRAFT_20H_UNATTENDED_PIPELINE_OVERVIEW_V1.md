# DRAFT — AWMA 20h Unattended Pipeline Handoff V1

Date: 2026-09-19

Status:

`PRE_REPAIR_DRAFT_NOT_EXECUTABLE`

This document is a pre-frozen coordination draft. It MUST NOT be executed before the current
`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1` report has been independently reviewed by ChatGPT
and a final handoff has replaced all placeholders below.

## 0. Why this draft exists

The current 174-new mainline is a scientific correctness gate around VM per-access coverage.
The next unattended campaign should not be designed from scratch after the repair result arrives.
This draft pre-freezes the pipeline structure, solve-and-continue policy, task queue, acceptance
contract, storage policy, and opportunity work. The final version should only:

1. bind exact post-repair branch / commit / binary / evidence identities;
2. choose the allowed post-repair branch among the decision cases;
3. enable/disable a small number of conditional tasks;
4. set the campaign deadline / launch metadata.

No new architecture mechanism is authorized by this draft.

## 1. Current frozen upstream

Current active mainline:

`AWMA_VM_PER_ACCESS_COVERAGE_REPAIR_174NEW_V1`

Coordination authority:

`hrl/awma-vm-per-access-coverage-repair-handoff-v1`

Coordination HEAD:

`8db8537c0bb837104b4ce5d56dec4b6b3b7e58fb`

Execution parent:

`hrl/awma-q05-global-access-determinism-174new-v1`

`be82faf264e93396b4b7d4fd72078c7e4491e3e4`

Current legacy translation status:

`LEGACY_VM_UNDERCOVERAGE_BASELINE_PENDING_REQUALIFICATION`

Current architecture-mechanism status:

`NOT AUTHORIZED`

109 accepted V2.1 anchor:

`hrl/awma-109-ten-hour-capture-native-recon-v2`

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Do not rewrite these accepted branches.

## 2. Final-version placeholders

The final handoff MUST replace:

`<POST_REPAIR_DECISION>`

`<POST_REPAIR_EXECUTION_BRANCH>`

`<POST_REPAIR_EXECUTION_SHA>`

`<POST_REPAIR_BINARY_SHA>`

`<POST_REPAIR_REQUALIFICATION_POLICY>`

`<CAMPAIGN_START_UTC>`

`<CAMPAIGN_DEADLINE_UTC>`

and MUST explicitly state which 174 opportunity tasks are enabled.

The final version MUST NOT infer a new repaired baseline merely because a repair completed.

## 3. Campaign structure

Two independent node lanes run concurrently after final authorization.

### Lane 174-new — correctness / requalification / consumer analysis

Priority order:

A. consume the already-reviewed repair decision;
B. execute only the approved minimal repaired-baseline requalification;
C. perform cross-family existing-evidence analysis;
D. conditionally run at most one non-Attention repaired R0/I0 screening pair.

174-new must never wait on new 109 data to complete A/B/C unless the final handoff explicitly
binds a new artifact dependency.

### Lane 109 — native characterization / experiment design validation

Priority order:

A. reuse accepted evidence and close missing native-resource characterization for selected
   existing families;
B. execute E1 shape × implementation diagnostics on Qwen2.5-7B raw/AWQ;
C. conditionally execute E3 natural-vs-controlled MoE routing diagnostics;
D. execute opportunistic tasks when budget remains:
   G1 scenario extension;
   G2 same-quantized-weight implementation decomposition;
   G3 profiling cache-control protocol sensitivity;
   G4 Llama raw shape-trend holdout;
E. bounded detailed capture only when pre-frozen trigger conditions are satisfied.

109 must not start new model downloads, new backend ports, or new architecture mechanisms.

## 4. Research-question mapping

The literature-audit-derived experiment roles are frozen as follows.

### E2 — execution-history sensitivity

Question:

> Can a kernel selected by function + shape be treated as representative without preserving
> relevant predecessor execution history?

This belongs primarily to the repaired 174 mainline because Q05 already has same-source
contiguous-prefix evidence. The repaired VM path must be qualified before quantitative
translation conclusions are reused.

### E1 — shape × low-bit implementation

Question:

> For the same semantic linear operator, how do shape and low-bit implementation jointly alter
> native performance and resource behavior?

This is the mandatory 109 side-lane scientific task.

Core matrix:

`{down_proj, q_proj} × {M=1, M=256} × {raw, AWQ}`

The matrix is a shape / implementation diagnostic. M=1 MUST NOT be relabeled as natural Decode.

### E3 — natural vs controlled MoE routing

Question:

> Does controlled expert-load input preserve the execution behavior relevant to MoE
> characterization?

This is conditional. Prefer natural N, histogram-preserving permutation P, and active-set
preserving balanced U-active. Artificial hotspot H and all-expert balancing are not required
in the first unattended campaign.

## 5. Solve-and-continue Goal policy

Each Codex window must run in GOAL MODE and treat the node-specific file as one continuous goal.

Engineering issues are solve-and-continue:

- build / compile;
- environment path;
- parser bugs;
- bounded profiler/tool retries;
- storage transfer resume;
- already-understood correctness-neutral scripting fixes;
- missing derived metadata that can be reconstructed from accepted authority.

Scientific issues are lane-local STOP boundaries:

- target identity changes;
- semantic operator binding changes;
- input / hidden / route authority changes;
- source / binary semantics change;
- result requires a different claim boundary;
- accepted experiment contract cannot be satisfied without approximation.

A lane-local scientific STOP does NOT automatically stop the other independent lane.
Freeze the affected task, emit evidence, and continue only with pre-authorized independent tasks.

Whole-campaign STOP is required for:

- shared accepted source corruption;
- node164 authority inconsistency affecting multiple tasks;
- GPU identity mismatch;
- lock / ownership conflict that cannot be resolved safely;
- evidence showing the final handoff scientific contract itself is invalid.

No task may silently weaken validation, fabricate operands/addresses/widths, or replace an
unavailable scientific target with a convenient one.

## 6. 20-hour budget policy

The final launcher will write a campaign timing manifest.

Nominal policy:

- active work may start at `<CAMPAIGN_START_UTC>`;
- no new GPU or simulator scientific target after `<CAMPAIGN_DEADLINE_UTC> - 2h`;
- reserve the final 2 hours for transfer, hash closure, node164 ACK, reports, review packs,
  commit, push, remote verify, clean worktrees, and lock release.

Tasks may finish early. Do not fill remaining time with unapproved sweeps.

Each opportunity task has its own hard budget and may be skipped if insufficient time remains.

## 7. Pipeline scheduling model

The pipeline is dependency-driven rather than a rigid sequential checklist.

A task becomes READY only when all required accepted authorities and gates are present.
A READY task can start as soon as its required resource is available.

Resources:

- `GPU109`: exclusive via `/data/c16/locks/c16_gpu_campaign.lock`;
- `CPU174`: simulator/analysis capacity;
- `STORE164`: durable large-artifact authority;
- `NET`: transfer path; may overlap CPU work but must not compromise hashes.

Examples of allowed overlap:

- 109 transfers an accepted bundle to 164 while CPU-only analysis runs;
- 174 parses existing accepted trace while 109 runs a native timing task;
- after a GPU task closes local hashes and enters transfer, the next GPU task may begin only
  if local disk / transfer pressure remains within the handoff limits and no data-authority
  ambiguity is introduced.

Examples of forbidden overlap:

- two 109 GPU owners;
- mutating the same accepted source/worktree from two tasks;
- concurrent writers to the same node164 accepted path;
- starting a detailed capture before its trigger decision is frozen.

## 8. Data and provenance

node164 remains authority for large raw / trace / durable scientific data.

109 may keep active model replicas and producer staging copies.

174-new stores only source/worktrees/binaries/bounded scratch/small evidence locally.

Accepted publication lifecycle remains:

`staging → ready → .partial transfer → size/hash verify → no-overwrite admit → receipt/ACK`

No accepted producer artifact is deleted in this campaign.

## 9. Forbidden work

Until separately authorized:

- no new TLB/PTW/PWC/cache architecture mechanism;
- no capacity/port/page-size/prefetch/speculation sweep;
- no simulator lookup constant calibration from RTX4080 native reconnaissance;
- no broad new model download;
- no DeepSeek MLA expansion;
- no OLMoE bring-up solely to fill idle time;
- no repeated Decode32 occurrence capture already covered by V2.1;
- no new pointer-chase/cg sweep without a new isolation method;
- no automatic full historical replay after VM repair.

## 10. Draft companion files

Read together:

- `DRAFT_20H_PIPELINE_SCHEDULER_POLICY_V1.md`
- `DRAFT_CODEX_GOAL_109_20H_PIPELINE_V1.md`
- `DRAFT_CODEX_GOAL_174NEW_POST_REPAIR_PIPELINE_V1.md`
- `DRAFT_20H_PIPELINE_ACCEPTANCE_CONTRACT_V1.md`

These files are drafts and are not executable until replaced or explicitly promoted by a
post-repair final coordination commit.
