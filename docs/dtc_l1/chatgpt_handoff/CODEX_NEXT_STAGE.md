# CODEX_NEXT_STAGE

## Status

**ACTIVE — BUFFERING × MEMORY-SERVICE INTERACTION; UNATTENDED SOLVE-AND-CONTINUE**

Do not restart the scientific program and do not reset any branch.

This specification supersedes the earlier rule that queue failure should immediately terminate downstream investigation. The accepted BICG/OO queue intervention changes the interpretation: queue capacity alone is insufficient, but a queue can be a buffering symptom of a slower downstream service path.

## Objective

Determine whether DTC performance under the original high injection cap can be recovered by:

1. queue buffering headroom;
2. one source-supported deeper memory-service headroom dimension;
3. or their interaction.

This remains a small bounded study, not a broad memory-system sweep.

## Source anchors

Before work:

1. `git fetch origin`.
2. Verify actual remote heads.
3. Use newer remote state if any branch advanced; record the delta, never reset.

Current review anchors:

- SG1: `e909f90a`
- SG3: `f1186336`
- SG5: `f4077f46`
- SG4A: use fetched latest remote read-only state.

Read:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. this file
4. SG3 Phase-A telemetry, queue execution plan, partial queue snapshot, and source/config audit files.

## Worktree / branch isolation

Execution/evidence branch:

`hrl/iscas2027-dtc-sg3-downstream-localization-v0`

Use the existing isolated SG3 worktree.

Treat SG1, SG4A, SG5, FAST64, Lane-E, and TC80 evidence as read-only.

Do not modify files in `docs/dtc_l1/chatgpt_handoff/`.

---

# Phase B — finish the already-authorized queue family

Do not stop or relaunch the already-running immutable attempts.

Current accepted partial row:

- BICG/OO queue=128: strict PASS
  - `MISS_QUEUE_FULL` 43,594,150 -> 0
  - cycles 47,231,655 -> 47,588,121 (+0.75%)
  - average lower lifetime 5,612.70 -> 5,692.26

Interpret this only as:

> queue capacity alone is insufficient for BICG/OO.

Do not interpret it as proof that queue pressure is irrelevant to a buffering × service interaction.

Let these existing rows terminate naturally and strict-validate immediately:

- BICG/IO queue=128
- GESUMMV/IO queue=128
- GESUMMV/OO queue=128

No new queue point is authorized.

---

# Phase C0 — zero-simulation memory-side source + telemetry audit

Run this analysis in parallel with the remaining Phase-B simulations.

**Do not launch a new memory-side simulator row until C0 is committed.**

## C0.1 Source-map the downstream path after the L2 miss queue

Audit current source and resolved FAST64 configuration for:

- memory-partition queues and admission;
- interconnect-to-memory path;
- DRAM scheduler queues;
- DRAM request/return queues;
- DRAM command/data path;
- DRAM timing/latency fields;
- memory bandwidth/service-width fields.

Record exact parser/source semantics and scope.

## C0.2 Extract existing accepted telemetry

From accepted BICG IO/OO:

- default cap=8192
- cap=2048
- cap=512

extract any source-defined metrics that actually exist for:

- memory-partition queue occupancy/full/stall;
- DRAM scheduler queue occupancy/full/stall;
- memory-fetch latency;
- DRAM queueing latency;
- DRAM service latency;
- memory bandwidth / data utilization;
- read/write command utilization/counts;
- interconnect-to-memory or partition stalls;
- DRAM bank activity/efficiency.

If a metric is not emitted or cannot be reconstructed exactly, write `NOT_AVAILABLE`.

Do not infer a counter from unrelated statistics.

## C0.3 Select at most one memory-service headroom knob

The selected knob must:

1. have source-proven semantics;
2. change one interpretable service-rate or service-latency dimension;
3. leave DTC semantics unchanged;
4. leave SM count, memory-channel count, L2-bank count, address mapping, trace identity, L2 capacity, L2 MSHR, and queue definition unchanged;
5. have at least some source/telemetry reason to be relevant;
6. be described as an idealized upper-bound headroom probe, not a production point.

Do not choose another queue-capacity knob as the M dimension.

Do not change multiple DRAM timing fields together.

Do not use perfect/infinite memory.

If no candidate satisfies all six rules, record:

`NO_CLEAN_MEMORY_SERVICE_HEADROOM_KNOB`

finish the queue family, build the review pack, and STOP without further simulation.

## C0 deliverables

Commit/push before any C1 run:

- `SG3_MEMORY_SIDE_SOURCE_MAP_V1.tsv`
- `SG3_BICG_MEMORY_SIDE_TELEMETRY_V1.tsv`
- `SG3_MEMORY_SERVICE_KNOB_SELECTION_V1.md`

The selection document must state:

- selected knob and exact default/headroom values;
- source semantics;
- what it changes;
- what it explicitly does not change;
- supporting telemetry;
- expected interpretation;
- forbidden overclaims.

---

# Phase C1 — predeclared BICG queue × memory-service 2×2

Only if C0 selects one valid memory-service knob.

For each mode IO and OO define:

- Q0M0 = queue32 + default memory service — existing accepted baseline
- Q1M0 = queue128 + default memory service — current/accepted Phase-B row
- Q0M1 = queue32 + selected memory-service headroom — NEW
- Q1M1 = queue128 + selected memory-service headroom — NEW

Thus at most **4 new BICG simulator rows** are authorized.

## Rolling launch rule

- Q0M1 for BICG IO/OO may launch immediately after C0 is committed.
- Q1M1 for a mode may launch only after that mode's Q1M0 queue=128 row has strict PASS.
- Do not wait for GESUMMV queue rows to finish before launching eligible BICG C1 rows.

All C1 rows keep:

- DTC cap = 8192
- default L2 capacity
- default L2 MSHR
- same L2 atom/line geometry
- same workload/trace identity
- same observer semantics

Only Q and the selected M dimension may differ according to the 2×2.

## Required C1 analysis

For each mode report:

- cycles
- cycle change vs Q0M0
- lower-request average/max lifetime
- queue-full / queue occupancy
- selected memory-side pressure metric(s)
- any other source-defined downstream stalls used in C0

Explicitly evaluate:

1. M-only effect: Q0M1 vs Q0M0
2. Q-only effect: Q1M0 vs Q0M0
3. Q+M effect: Q1M1 vs Q0M0
4. interaction: whether Q1M1 provides additional recovery beyond the better single intervention

No causal statement before strict PASS of the needed cells.

---

# Phase C2 — bounded GESUMMV independent validation

GESUMMV is not an automatic full 2×2.

Use a predeclared 5% paper-relevance gate, set **before** any C1 memory-headroom result:

### Gate M — memory-service-alone validation

If either BICG IO or OO Q0M1 reduces cycles by **>=5%** versus its Q0M0 baseline, with the selected service-pressure telemetry moving coherently, authorize:

- GESUMMV IO Q0M1
- GESUMMV OO Q0M1

Total: 2 rows.

### Gate I — interaction validation

If either BICG mode's Q1M1 provides an additional **>=5% cycle reduction relative to the better of Q0M1 and Q1M0**, with coherent telemetry, authorize in addition:

- GESUMMV IO Q1M1
- GESUMMV OO Q1M1

Total: 2 additional rows.

Therefore C2 adds:

- 0 rows if neither gate is met;
- 2 rows for memory-service-alone validation;
- at most 4 rows if a queue × memory interaction also merits validation.

Use the same selected M knob/value. No new memory parameter values.

Keep at most two heavy GESUMMV simulator processes concurrently.

---

# Explicitly forbidden scope

Do NOT launch:

- additional L2 capacity points
- additional L2 MSHR points
- cap=1024 or cap=4096
- queue=64
- L2 data/fill-port experiments unless C0 explicitly selects that exact port as the single M service dimension under its source/telemetry criteria
- more than one memory-service knob
- memory-channel-count changes
- L2-bank-count changes
- address-mapping changes
- broad ROP / NoC / DRAM sweeps
- multi-parameter DRAM timing sweeps
- perfect/infinite memory
- extra logical-Tag experiments
- FAST12 sensitivity sweeps
- new adaptive-admission mechanism

Do not retry the SG5 GESUMMV/IO observer a third time.

---

# Acceptance requirements for every new row

- fresh UUID
- immutable run directory
- exact Core commit
- exact runtime SHA
- exact ordered config-chain SHA
- exact trace identity
- START receipt
- terminal receipt
- strict validation receipt
- terminal drain / observer closure checks

Preserve every failure. Never overwrite an attempt.

A validator invocation/input error may use same-output named revalidation, preserving the original FAIL receipt.

---

# Paper-safe decision classes

At final closure choose the strongest supported bounded status:

- `MEMORY_SERVICE_HEADROOM_SUPPORTED`
- `BUFFERING_MEMORY_SERVICE_INTERACTION_SUPPORTED`
- `MEMORY_SERVICE_HEADROOM_PARTIAL`
- `QUEUE_AND_SELECTED_MEMORY_SERVICE_INSUFFICIENT`
- `NO_CLEAN_MEMORY_SERVICE_HEADROOM_KNOB`

Do not claim a unique global GPU bottleneck beyond tested BICG/GESUMMV evidence.

---

# Resource policy

The user authorizes aggressive compute use and will manage disk capacity.

- Do not use old fixed free-space bands as automatic stop criteria.
- Record free space and projected growth.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- Lightweight analysis and BICG rows may use remaining safe workers.

---

# Deliverables

Create/update a review pack under:

`docs/dtc_l1/review_packs/DOWNSTREAM_HEADROOM_<revision>/`

with at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- Phase-A BICG telemetry
- completed queue-family results
- memory-side source map
- memory-side telemetry table
- M-knob selection receipt
- BICG 2×2 results if executed
- GESUMMV validation results if triggered
- exact paper-safe claims
- forbidden overclaims
- raw-log index only, not large raw logs

Update:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

with final branch SHA, status, review-pack entry point, evidence summary, and remaining issues.

---

# STOP boundary

Complete:

1. remaining queue-family terminal disposition;
2. C0 source/telemetry audit;
3. any C1/C2 rows authorized by the predeclared gates;
4. review pack;
5. Codex handoff;
6. commit and push.

Then STOP.

Stop earlier only if continuing would require changing:

- scientific identity;
- DTC semantics;
- frozen evidence;
- the one-knob experiment definition after C0 registration;
- claim boundary;
- or introducing a new architecture mechanism.
