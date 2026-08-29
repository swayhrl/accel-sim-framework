# EP-L2 ChatGPT Handoff — CODEX_NEXT_STAGE

Status: C7d has already been launched. **Do not restart it.**

Use this file as the completion checklist for the in-progress C7d work.

Read first:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/chatgpt_handoff/C7D_DISCUSSION_REFERENCE.md
```

## Objective

Complete:

```text
C7d Target Characterization Completeness
```

The objective is that the next clean `13 x 2 @850 MHz` campaign is the only full Target-Baseline characterization rerun needed.

C7d is instrumentation-only.

## Isolation

The live C6c smoke/prefill campaign may continue unchanged.

Do not modify, rebuild, clean, reset, or reuse its worktrees, binaries, or results.

C7d must use independent worktrees/branches derived from:

```text
Core base:
0cde333340792cffed869cbbc7e7dc88667c6b8b

Framework base:
0a0c0fc3e1ffb6ca346090e59e94d2128e5adc0e
```

Suggested branches:

```text
Core:      hrl/ep-l2-c7d-char-v0
Framework: hrl/ep-l2-c7d-char-v0
```

## Do not change architecture semantics

Do not change cache behavior, tag replacement, MSHR/descriptor capacities or lifetime, WAD semantics, payload capacities, payload banking timing, L1 configuration, queue capacities, DRAM timing/scheduler, Unified, RO, or TVD behavior.

## Required telemetry

### Tag / set

```text
line-allocation eligible
line-allocation blocked
all-reserved/set-allocation failure
reserved lines avg/p95/max
max reserved ways in one set
```

### Line MSHR / descriptors

Separately emit:

```text
EP_L2_BLOCK_LINE_MSHR_FULL
EP_L2_BLOCK_DESCRIPTOR_POOL_FULL
EP_L2_BLOCK_PER_ADDRESS_CAP
```

Add:

```text
line_mshr_alloc_eligible
line_mshr_full_block
descriptor_alloc_eligible
descriptor_pool_full_block
per_address_cap_eligible
per_address_cap_block
descriptor_chain_depth avg/p95/max/histogram
```

### WAD

Use exact production events:

```text
WAD_FULL events
same-address WAD hazard events
same-address wait cycles
WAD lifetime avg/p95/max
WAD occupancy avg/p95/max
```

### Payload

Separate:

```text
resident live avg/p95/max
resident VALID
resident DIRTY
resident pending-sector count
bypass pending
bypass ready
payload service-port denial
payload capacity/allocation denial
```

### C6c bank telemetry

Use:

```text
bank_logical_ops
bank_attempts
bank_grants
bank_retry_attempts
bank_true_conflict_ops
bank_true_conflict_events
bank_wait_cycles
```

Primary conflict rate:

```text
bank_true_conflict_ops / bank_logical_ops
```

Add per-bank logical ops/grants/conflicts/wait and, where practical, operation classes:

```text
resident-hit-read
resident-write
fill-write
WB-readout
bypass-fill
bypass-read
```

Kernel bank telemetry must be true interval delta.

### L1 bottleneck audit

Reuse native L1 counters only when semantically exact and stable. Final output should distinguish as far as simulator semantics allow:

```text
MSHR entry full
merge full
MissQ full
bank/port conflict
line allocation
```

If native statistics are insufficient, add lightweight timing-neutral target counters.

### Lower / memory path

Separate:

```text
MissQ occupancy/full/block
L2->DRAM FIFO occupancy/full/block
FR-FCFS scheduler avg/max/full/block
DRAM ReturnQ occupancy/full/block
DRAM->L2 FIFO occupancy/full/block
L2->ICNT / ICNT->L2 where relevant
DRAM read transactions/bytes
DRAM write transactions/bytes
DRAM bandwidth utilization
```

Prefer trustworthy existing native DRAM counters where possible.

### Temporal characterization

Add lightweight 5K-cycle windows for:

```text
line MSHR
descriptors
WAD
payload
bank true contention/wait
MissQ
L2->DRAM
scheduler occupancy
```

Do not reproduce the full historical L2CHARV1 collector.

## Schema / parser / analyzer

Extend `EPL2B0V1` conservatively. Existing fields keep their old meaning; add explicitly named exact fields.

Update:

```text
util/ep_l2/parse_epl2_b0.py
util/ep_l2/analyze_target_baseline.py
```

Eliminate invalid mappings:

```text
block_descriptor -> descriptor_pool_full
block_wad        -> WAD_full
block_lower      -> scheduler_block
generic payload_block -> payload_capacity_block
```

Use:

```text
true bank conflict rate = bank_true_conflict_ops / bank_logical_ops
```

and consume `bank_wait_cycles`.

## Validation

C7d cannot close until:

```text
full Release build
C3-C7 + C6c regressions
new exact-blocker directed regressions
parser/schema regressions
EPL2B0V1 OFF vs ON exact simulated timing neutrality
sequential multi-kernel additive-delta check
kernel bank interval-delta check
terminal invariants unchanged
git diff --check
clean worktrees
```

Measure and report host overhead on one short/medium representative run.

## Out of scope

Do not implement:

```text
RO oracle
RO shadow
TVD shadow
Unified borrowing
graphics bypass classification
1GHz experiments
```

Existing C6c smoke/prefill may finish as diagnostic evidence. If C7d changes Core SHA, do not promote those runs into the final formal Target-Baseline dataset.

## Deliverables

Produce:

```text
docs/ep_l2/C7D_CHARACTERIZATION_CLOSEOUT.md
docs/ep_l2/C7D_TELEMETRY_SOURCE_MAP.md
docs/ep_l2/C7D_SCHEMA.md
```

Use scoped semantic commits.

At the end, place ChatGPT review material under:

```text
docs/ep_l2/review_packs/
```

Include source map, schema, changed-file/diff summary, directed regressions, parser/analyzer tests, OFF/ON timing-neutrality evidence, host-overhead measurement, manifests, and SHA256SUMS.

Exclude large raw logs; include a raw-log index.

Push Core C7d and Framework review material to remote.

Report:

```text
final Framework/Core SHAs
worktree/branch names
validation summary
unresolved telemetry gaps
review-pack path
recommended GitHub files for ChatGPT to inspect
```

Then STOP before the final clean 26-run campaign.
