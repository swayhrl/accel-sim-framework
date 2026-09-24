# CODEX_NEXT_STAGE

## Status

**ACTIVE — MEMORY-SIDE QUEUE-CHAIN + DRAM-SERVICE HEADROOM; UNATTENDED SOLVE-AND-CONTINUE**

Do not restart the scientific program and do not reset any branch.

This specification supersedes the earlier STOP after `QUEUE_AND_SELECTED_MEMORY_SERVICE_INSUFFICIENT`. The accepted queue results remain final evidence, but the accepted busW probe is reclassified as diagnostic/non-discriminating for the dominant 32-B sector-read service question.

## Objective

Answer one bounded question:

> Can finite queues later in the L2->memory path, alone or together with a genuine detailed-DRAM service-rate upper bound, explain why BICG/GESUMMV benefit so strongly from DTC injection throttling?

This is one predeclared queue-chain/service study, not an open-ended memory sweep.

## Source anchors

Before work:

1. `git fetch origin`.
2. Verify actual remote heads.
3. Use newer remote state if any branch advanced; record the delta, never reset.

Current review anchors:

- SG1: `e909f90a`
- SG3: `2c5802153b30f73ebabb5ad69dc44de055cd0497`
- SG4A: `7c0a90e`
- SG5: `f4077f46`

Read in order:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. this file
4. `docs/dtc_l1/review_packs/DOWNSTREAM_HEADROOM_V1/`
5. SG3 Phase-A/queue/C0 source-map files.

## Worktree / branch isolation

Execution/evidence branch:

`hrl/iscas2027-dtc-sg3-downstream-localization-v0`

Use an isolated SG3 worktree.

Treat SG1, SG4A, SG5, FAST64, Lane-E, TC80, accepted queue=128 rows, and accepted busW rows as immutable/read-only evidence.

Do not modify files in `docs/dtc_l1/chatgpt_handoff/`.

---

# R0 — no-simulation semantic correction and source/telemetry audit

Complete R0 before launching any new row.

## R0.1 Reclassify busW evidence

Record, without deleting any run, that:

- L2 sector atom = 32 B;
- dominant sector-read DRAM request size = 32 B;
- default `dram_atom_size = BL(2) * busW(16 B) * chips(1) = 32 B`;
- a 32-B request already completes in one detailed-DRAM data step;
- `busW 16->32` therefore does not provide a discriminating 2x transfer-step reduction for that path.

The accepted busW rows remain valid diagnostic evidence but must not support the claim “2x DRAM service rate is insufficient.”

## R0.2 Confirm queue-chain semantics

Source-audit and record exact semantics/default sizes for:

- L2-internal miss queue = 32/bank;
- `gpgpu_dram_partition_queues` order and sizes:
  - ICNT->L2 = 64
  - L2->DRAM = 64
  - DRAM->L2 = 64
  - L2->ICNT = 64
- FR-FCFS scheduler queue = 64/channel;
- DRAM return queue = 192/channel;
- memory-partition shared-credit formula and its dependence on scheduler/return queue capacities;
- DRAM clock-domain semantics at 850 MHz.

## R0.3 Existing telemetry

From accepted BICG IO/OO default, cap2048, and cap512 rows, extract where available:

- `L2_dram_queue_full`;
- DRAM `mrqq` maximum and average;
- `gpu_stall_icnt2mem`;
- `gpu_stall_mem2icnt`;
- mean memory-fetch latency;
- mean ICNT->memory latency;
- mean MRQ latency;
- DRAM bandwidth/utilization;
- DRAM bank/command statistics.

Use `NOT_AVAILABLE` where a metric is not source-defined/emitted.

R0 is descriptive only; it does not gate the six predeclared BICG families.

## R0 deliverables

Commit/push:

- `SG3_MEMORY_QUEUE_CHAIN_SOURCE_MAP_V2.tsv`
- `SG3_BICG_MEMORY_QUEUE_CHAIN_TELEMETRY_V2.tsv`
- `SG3_BUSWIDTH_PROBE_RECLASSIFICATION_V1.md`
- `SG3_MEMORY_QUEUE_CHAIN_EXECUTION_PLAN_V1.tsv`

No simulation before this commit.

---

# R1 — six predeclared BICG headroom families

Run every family for:

- BICG IO
- BICG OO

Thus R1 contains exactly **12 new simulator rows**.

All rows keep:

- DTC cap = 8192
- 64 SM
- 20 memory channels
- 40 L2 subpartitions
- same address mapping
- same trace identity
- default L2 MSHR
- default L2 line/sector geometry
- same observer semantics
- Core/runtime identity unchanged except config-only overlays

### Family A — L2->DRAM queue headroom

Change only:

`gpgpu_dram_partition_queues 64:64:64:64 -> 64:256:64:64`

### Family B — DRAM scheduler/admission headroom

Change:

`gpgpu_frfcfs_dram_sched_queue_size 64 -> 256`

Keep DRAM return queue at 192.

Document that the source-defined memory-partition shared-credit limit changes as a consequence; report this as scheduler/admission headroom, not a pure storage-only effect.

### Family C — return-path buffering headroom

Change together:

- `gpgpu_dram_partition_queues 64:64:64:64 -> 64:64:256:64`
- `gpgpu_dram_return_queue_size 192 -> 768`

This is a bundled serial return-path upper bound.

### Family D — full memory-side queue-chain headroom

Change:

- L2-internal miss queue: 32 -> 128
- L2->DRAM queue: 64 -> 256
- DRAM scheduler queue: 64 -> 256
- DRAM return queue: 192 -> 768
- DRAM->L2 queue: 64 -> 256

Keep ICNT->L2 and L2->ICNT at 64.

### Family E — detailed-DRAM 2x service-rate headroom

Change only the DRAM clock:

`gpgpu_clock_domains 1410:1410:1410:850 -> 1410:1410:1410:1700`

Keep:

- busW=16 B
- BL=2
- DRAM timing cycle counts unchanged
- queue sizes default
- L2 resources default
- channels/mapping unchanged

Interpretation boundary:

> idealized 2x detailed-DRAM service-rate/time-domain upper bound, not a physical product frequency point.

### Family F — full queue-chain + DRAM2x

Combine Family D + Family E.

## R1 launch policy

After R0 static validation and commit:

- place all 12 rows into the rolling worker pool immediately;
- do not wait for one family to finish before launching another;
- row-local strict validation on terminal;
- preserve failed attempts and retry only under existing immutable-attempt rules;
- no result-dependent new family.

---

# R2 — BICG analysis

For every accepted family/mode, report:

- cycles and speedup vs exact default;
- lower-request average/max lifetime;
- DTC outstanding average if available;
- L2-internal queue-full and occupancy;
- `L2_dram_queue_full`;
- DRAM `mrqq` max/avg;
- ICNT/memory stall counters;
- memory/MRQ latency;
- queue/service parameters.

Interpret each family only within its source semantics.

Explicitly distinguish:

- single queue-stage headroom;
- scheduler/admission headroom;
- response buffering;
- all-buffering headroom;
- DRAM service-rate headroom;
- buffering + service interaction.

---

# R3 — bounded GESUMMV independent validation

Do not run the full six-family GESUMMV matrix.

A BICG configuration is eligible if:

- it reduces cycles by >=5% in either IO or OO versus exact default;
- telemetry changes coherently;
- it is one of Families A-F.

Validate at most **two configurations**, using this fixed priority if multiple qualify:

1. Family F — full queue-chain + DRAM2x
2. Family D — full queue-chain
3. Family E — DRAM2x
4. Family A — L2->DRAM queue
5. Family B — scheduler/admission
6. Family C — return-path buffering

For each selected configuration run:

- GESUMMV IO
- GESUMMV OO

Thus R3 adds 0, 2, or at most 4 rows.

Keep at most two heavy GESUMMV simulator processes concurrently.

---

# R4 — conditional all-headroom ceiling with L2 capacity

The existing L2-capacity=2x BICG evidence already shows partial benefit.

Only if Family F improves BICG by >=5% in either IO or OO, authorize exactly two additional BICG ceiling rows:

- L2 capacity = 20 MiB (existing accepted 2x-capacity definition)
- Family D full queue-chain headroom
- DRAM = 1700 MHz
- IO
- OO

No other capacity level and no factorial expansion.

Interpret these only as an idealized all-headroom ceiling.

---

# Explicitly forbidden scope

Do NOT launch:

- L2-internal miss queue >128
- L2->DRAM / DRAM->L2 / scheduler queues beyond 256
- DRAM return queue beyond 768
- new L2 MSHR points
- cap=1024 or cap=4096
- additional DRAM frequencies
- busW as the formal memory-service dimension
- memory-channel-count changes
- L2-bank-count changes
- address-mapping changes
- ICNT->L2 or L2->ICNT queue sweeps
- L2 data/fill-port sweeps
- NoC or ROP sweeps
- DRAM timing-string sweeps
- perfect/infinite memory
- adaptive admission mechanism
- FAST12 sensitivity
- new logical-Tag experiments

Do not retry the SG5 GESUMMV/IO observer.

---

# Acceptance requirements

For every new row:

- fresh UUID
- immutable run directory
- exact Core commit
- exact runtime SHA
- exact ordered config-chain SHA
- exact trace identity
- START receipt
- natural terminal receipt
- strict validation receipt
- terminal drain / observer closure checks

Preserve every failure. Never overwrite an attempt.

---

# Paper-safe final statuses

Use the strongest supported bounded status:

- `MEMORY_QUEUE_STAGE_HEADROOM_SUPPORTED`
- `MEMORY_QUEUE_CHAIN_HEADROOM_SUPPORTED`
- `DRAM_SERVICE_RATE_HEADROOM_SUPPORTED`
- `QUEUE_CHAIN_DRAM_SERVICE_INTERACTION_SUPPORTED`
- `MEMORY_DOWNSTREAM_HEADROOM_PARTIAL`
- `MEMORY_QUEUE_CHAIN_AND_DRAM2X_INSUFFICIENT`

Do not claim a unique global GPU bottleneck beyond tested BICG/GESUMMV scope.

---

# Deliverables

Create a new review pack:

`docs/dtc_l1/review_packs/MEMORY_QUEUE_CHAIN_DRAM_HEADROOM_V1/`

with at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- R0 source map / telemetry / busW reclassification
- R1 execution matrix and accepted results
- R2 analysis
- any R3 GESUMMV validation
- any R4 all-headroom ceiling
- exact paper-safe claims
- forbidden overclaims
- raw-log index only

Update:

`docs/dtc_l1/codex_handoff/LATEST_REPORT.md`

with final branch SHA, status, review-pack entry point, evidence summary, and remaining issues.

---

# Resource policy

The user authorizes aggressive compute use and will manage disk capacity.

- Do not use old fixed free-space bands as automatic stop criteria.
- Record free space and projected growth.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- BICG rows and analysis may use remaining safe workers aggressively.

---

# STOP boundary

Complete:

1. R0 source/telemetry audit and execution-plan registration;
2. all 12 R1 BICG rows;
3. R2 analysis;
4. any R3/R4 rows authorized by the predeclared gates;
5. review pack;
6. Codex handoff;
7. commit and push.

Then STOP.

Stop earlier only if continuing would require changing:

- scientific identity;
- DTC semantics;
- frozen evidence;
- the predeclared queue/service family definitions;
- claim boundary;
- or introducing a new architecture mechanism.
