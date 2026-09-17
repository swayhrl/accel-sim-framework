# CODEX NEXT STAGE — 174-new Q05 Warm-Replay Feasibility V1

## Status

ACTIVE MAINLINE.

Stage:

`AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1`

Node:

```text
174-new / port 2239
```

This stage audits and qualifies the simulator methodology required to run real predecessor kernels before Q05 without accidentally resetting the very state being studied.

It is NOT yet the real predecessor warmup experiment.

## Start point

Read the ChatGPT coordination branch first:

`hrl/awma-q05-context-warmup-handoff-v1`

Mandatory files:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTEXT_WARMUP_EXPERIMENT_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Preferred parent:

```text
hrl/awma-q05-translation-timeline-174new-v1
reported completion commit = 6319020c
```

First verify that this branch/commit is visible from the configured remote and that its review pack/report are present. If the reported execution commit is not remotely resolvable, do not silently substitute another provenance chain. Resolve the Git provenance first or STOP_FOR_ENGINEERING_PROVENANCE_REVIEW.

Recommended execution branch:

`hrl/awma-q05-warm-replay-feasibility-174new-v1`

## Frozen science

Keep read-only:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT / B1 / T2048 / Decode32 / FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
function occurrence 0
```

Existing Q05 SIM_INPUT/baseline/run/evidence IDs remain read-only.

Accepted isolated R0 and timeline results remain comparison anchors, not warm-context claims.

## Scientific objective

Prove exactly what simulator state survives a kernel boundary and establish a trustworthy measurement method for:

```text
predecessor prefix
-> preserved modeled state
-> Q05 measurement boundary
-> Q05-only statistics
```

Answer:

1. Does the current trace-driven execution reuse one simulator instance across kernels?
2. Which state is reset by `init()`, per-grid reinit, trace-driver plumbing, or kernel completion?
3. Which TLB/PWC/cache structures persist today?
4. Can Q05-only statistics be measured by snapshots/deltas without resetting warm state?
5. Can a diagnostic two-kernel sequence prove the intended persistence behavior?
6. What exact same-run trace/address contract will be required for the later real predecessor replay?

---

## D0 — Remote/provenance and source audit

Before code changes:

- verify the reported timeline branch/commit and review pack;
- record framework/core/submodule SHAs;
- record simulator binary used by the accepted isolated Q05 result;
- identify the trace-driven kernel dispatch loop and all per-kernel initialization calls;
- identify construction/destruction lifetime of the VM translation controller;
- identify construction/destruction/reset lifetime of L1 data caches, shared L2 data cache, TLBs and PWC;
- identify any cache/TLB flush/shootdown invoked at a kernel/grid boundary;
- identify whether outstanding memory traffic is drained before next kernel dispatch.

Use actual source. Do not infer persistence from class ownership alone.

Output:

`SOURCE_AUDIT_KERNEL_BOUNDARY_STATE.md`

---

## D1 — Kernel-boundary state matrix

Build a source-backed table for at least:

```text
shader pipeline/CTA state
register/shared-memory per-CTA state
L1 data cache
shared L2 data cache
L1 TLB
L2 TLB
PWC
translation MSHR
PWQ
active walkers/PTE requests
DRAM queues
interconnect queues
replacement/LRU metadata
translation generations/ASID state
```

For each component record separately:

```text
state at end of kernel
what function touches it at next-kernel start
classification:
  PERSISTS_BY_SOURCE
  RESET_BY_SOURCE
  DRAINED_BUT_METADATA_PERSISTS
  NOT_MODELED
  UNKNOWN
```

Do not assume the simulator behavior is identical to RTX4080 hardware behavior.

Output:

`KERNEL_BOUNDARY_STATE_MATRIX.tsv`

---

## D1B — Carry-forward page-key reconciliation

Before a future native page-overlap set is joined to simulator keys, reconcile the previous structural mismatch:

```text
offline full-Q05 unique 64KiB VPN = 228
full simulator translation keys    = 240
```

Using the existing trace/timeline evidence and source semantics, compute:

```text
intersection
simulator-only keys
trace/offline-only pages
reason category per difference when provable
```

Possible reasons must be demonstrated, not guessed (e.g. access crossing, scope differences, address classes, key semantics).

If exact reconciliation is not possible, define a safe join contract and preserve UNKNOWN differences.

Output:

```text
Q05_PAGE_KEY_RECONCILIATION.tsv
Q05_PAGE_KEY_RECONCILIATION.md
```

This is important because the next native context track will report predecessor page overlap.

---

## D2 — Measurement-boundary design

Design a target-only measurement method that preserves warm state.

Preferred method:

```text
run prefix normally
snapshot monotonically meaningful counters immediately before Q05
run Q05
snapshot immediately after Q05
Q05 metric = after - before
```

Audit every required metric to ensure delta semantics are valid.

Do NOT call a reset method at Q05 entry merely because it resets statistics. Some simulator init/update routines may also touch architectural/microarchitectural state.

If an existing stats API can safely mark a kernel boundary without clearing persistent state, use it.

If not, a diagnostic-only snapshot/export path may be added, provided it is:

```text
disabled by default
read-only with respect to simulated state
no scheduler/timing/queue/replacement changes
```

Any diagnostic binary requires a neutrality gate against the accepted isolated Q05 run before scientific use.

Output:

`Q05_MEASUREMENT_BOUNDARY_CONTRACT.md`

---

## D3 — Diagnostic state observability

For the future warmup study, determine whether the simulator can observe at Q05 entry, without changing state:

```text
L1 TLB occupancy / resident translation keys by SM if practical
L2 TLB occupancy / resident keys
PWC occupancy / relevant prefix identities
translation MSHR/PWQ/walker quiescence
L1/L2 data-cache aggregate occupancy/hit counters when source-supported
```

Full cache-content dumping is not mandatory.

The minimum translation-state observability should allow later questions such as:

> how many Q05 translation keys are already resident at target entry?

If key dumping itself would change timing/state, do not implement it; define a safe alternative.

Output:

`WARM_STATE_OBSERVABILITY.md`

---

## D4 — Self-warm plumbing diagnostic

Only after D0-D3 source audit, perform a diagnostic proof-of-plumbing if the current simulator supports sequential multi-kernel execution without semantic changes.

Preferred diagnostic:

```text
Q05 #1 -> Q05 #2
```

using a local diagnostic fixture derived from the accepted Q05 trace/address identity.

Purpose:

- prove whether state actually survives kernel dispatch;
- prove Q05 #2 can be measured independently by counter deltas;
- expose accidental resets.

Label every output:

`SELF_WARM_DIAGNOSTIC_ONLY`

It is NOT a model-context experiment and must not be reported as realistic Q05 warm performance.

Compare at least:

```text
isolated Q05
first Q05 in pair
second Q05 in pair
```

Where available report:

```text
cycles
translation L1/L2 access/hit/miss
walks
PWC
PTE traffic
translation MSHR merges/wait
Q05 target-entry resident-key counts
cache traffic/hits in proven units
```

If current framework necessarily reconstructs/reset the simulator between kernels, do not patch that silently. Record:

`SIMULATOR_KERNEL_BOUNDARY_RESET_BLOCKER`

and STOP_FOR_SCIENTIFIC_REVIEW before implementing a new state-persistence semantic.

---

## D5 — Address/context continuity contract for real predecessor replay

Define the exact future input requirement for node109 predecessor traces.

At minimum require:

```text
one frozen workload/model/input identity
one ordered contiguous kernel sequence
same-run address context or a formally proven remapping contract
per-kernel exact function + occurrence + grid/block
context/ASID policy
no missing interior kernels
trace terminal/grammar closure for every member
```

Do not approve a plan that concatenates independent-process absolute virtual addresses without a remapping proof.

Specify how the later simulator driver should ingest an ordered multi-kernel context bundle and where the Q05 measurement boundary sits.

Output:

`PREDECESSOR_CONTEXT_BUNDLE_CONTRACT.md`

---

## D6 — Future warm-prefix experiment matrix proposal

Do not run the real experiment yet.

Prepare a bounded matrix template for the next stage, to be populated after node109 reports actual prefix overlap.

Expected rows conceptually:

```text
ISOLATED_Q05
SHORT_PREFIX + Q05
MEDIUM_PREFIX + Q05
FULL_AVAILABLE_PREFIX + Q05
```

For each future row define the metrics that must be compared:

```text
Q05 cycles / completed active thread-instructions
Q05 translation keys first-seen within Q05
Q05 keys already resident at entry when observable
L1/L2 TLB hits/misses
walk count
PWC/PTE activity
requester latency decomposition
fanout/merge behavior
L2/DRAM data traffic where valid
```

No prefix capture or scientific warm replay is authorized by this template alone.

Output:

`WARM_PREFIX_EXPERIMENT_TEMPLATE.tsv`

---

## D7 — Required decision

Final report must classify simulator readiness as one of:

```text
WARM_REPLAY_READY_WITH_EXISTING_STATE_SEMANTICS
WARM_REPLAY_READY_WITH_DIAGNOSTIC_COUNTER_BOUNDARY_ONLY
SIMULATOR_KERNEL_BOUNDARY_RESET_BLOCKER
ADDRESS_CONTEXT_CONTRACT_BLOCKER
INCONCLUSIVE
```

Directly answer:

1. What persists across kernels today?
2. What is intentionally reset/drained?
3. Can statistics be separated without clearing warm state?
4. Did the self-warm diagnostic prove actual state persistence?
5. Can future same-run predecessor traces be replayed continuously under the current simulator semantics?
6. What exact engineering/scientific blockers remain before real prefix+Q05 runs?

---

## Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1/
```

At minimum:

```text
README.md
SOURCE_ANCHORS.md
SOURCE_AUDIT_KERNEL_BOUNDARY_STATE.md
KERNEL_BOUNDARY_STATE_MATRIX.tsv
Q05_PAGE_KEY_RECONCILIATION.tsv
Q05_PAGE_KEY_RECONCILIATION.md
Q05_MEASUREMENT_BOUNDARY_CONTRACT.md
WARM_STATE_OBSERVABILITY.md
SELF_WARM_DIAGNOSTIC.md
PREDECESSOR_CONTEXT_BUNDLE_CONTRACT.md
WARM_PREFIX_EXPERIMENT_TEMPLATE.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Large diagnostic raw remains on node164.

## STOP conditions

STOP for scientific review if continuing would require:

- changing TLB/cache/PTW functional or timing semantics merely to preserve state;
- deciding unproven RTX4080 kernel-boundary behavior by assumption;
- resetting state at Q05 measurement boundary;
- stitching unrelated address spaces;
- changing accepted Q05 identity/SIM_INPUT;
- beginning real predecessor simulator-native capture or real warm-prefix science before node109 context evidence returns.

Routine source navigation, parser, build, diagnostic output and Git issues are solve-and-continue.

## Completion

Expected marker:

`AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1_COMPLETE_WITH_SCOPE`

Then review pack -> report -> hashes -> commit -> push -> remote verify -> clean worktree -> STOP.
