# EP-L2 C7e Implementation Handoff

Status: authorized as the last source-changing instrumentation/readiness stage before the final Target-Baseline campaign.

Read together with:

```text
CURRENT_STATE.md
C7E_DISCUSSION_REFERENCE.md
C7E_ACCEPTANCE_CRITERIA.md
CODEX_TARGET_GOAL.md
```

## Objective

Complete `C7e Final Target-Characterization Readiness` from the reviewed C7d pair:

```text
Core base      88e243e8e421002079adc85b9efae3452c02a828
Framework base 2aef9fad48207415a9697f9b891068b42008e0a8
```

Use isolated branches/worktrees, suggested:

```text
Core      hrl/ep-l2-c7e-final-char-v0
Framework hrl/ep-l2-c7e-final-char-v0
```

C7e is instrumentation/provenance only. It must not change modeled Target-Baseline behavior.

## Frozen functional scope

Do not change:

```text
L2 geometry/replacement
MSHR line-entry capacity or lifetime
request-descriptor capacity/lifetime
per-address cap
WAD functional semantics
payload capacity/ownership
C6d bank-arbitration timing or semantics
L1 configuration
queue capacities
DRAM timing/scheduler policy
850 MHz primary target
Unified borrowing
RO mechanisms/oracle
TVD
1 GHz experiments
```

## Mandatory implementation work

### 1. L1D-only Target telemetry

Add a GPU-scope timing-neutral L1D-only schema/output, preferably `EPL2L1V1`.

Do not aggregate L1I/L1C/L1T into it and do not duplicate one GPU-global L1 value into every L2 slice.

At minimum provide application cumulative and kernel launch-to-completion delta records for:

```text
L1D accesses
L1D misses
LINE_ALLOC_FAIL
MISS_QUEUE_FULL
MSHR_ENTRY_FAIL
MSHR_MERGE_FAIL
MSHR_RW_PENDING
L1D bank/latency-queue conflict
```

Use exact native failure classes where their semantics are stable. Source the real L1D bank/latency-queue conflict path rather than inferring it from generic reservation failure.

Parser output:

```text
target_l1.csv
```

### 2. Correct Tag-way denominator

Preserve compatibility fields but add exact new-way demand fields:

```text
c7e_tag_way_alloc_need
c7e_tag_way_alloc_block
```

A `SECTOR_MISS` on an already-resident line must not count as a new Tag-way allocation need.

### 3. Independent MSHR/descriptor/cap demand denominators

Keep exact blocker fields from C7d. Add independent demand denominators:

```text
c7e_line_mshr_need
    = request semantically needs a new line MSHR

c7e_descriptor_need
    = request semantically needs one persistent requester descriptor

c7e_per_address_cap_check
    = request merges into an existing address chain and checks the 32/address cap
```

These denominators must be independent of which blocker wins `full_reason()` priority.

### 4. WAD kernel-lifetime semantics

Make completed-WAD lifetime statistics true kernel launch-to-completion deltas, or explicitly emit them as unavailable for kernel scope. Never label application-cumulative lifetime as kernel interval data.

### 5. DRAM/lower semantic repair

Separate:

```text
issue/head attempts
actual successful read issues
actual successful write/WB issues
actual successful read bytes
actual successful write bytes
```

Successful issue counters increment only when the request actually leaves L2->DRAM arbitration and enters the DRAM-latency/DRAM path.

Keep distinct:

```text
DRAM internal ReturnQ / channel
per-slice DRAM->L2 FIFO
```

Do not name a `dram_L2_queue_full()` condition as internal ReturnQ full.

Separate scheduler observation from causal blocking:

```text
scheduler_full_observed
scheduler_causal_block
```

`causal_block` means the request could otherwise issue but the scheduler queue is full.

### 6. Channel-scope time-weighted DRAM telemetry

Add a channel-scope timing-neutral schema/output, preferably `EPL2DRAMV1`, sampled over DRAM cycles.

At minimum provide application cumulative values for:

```text
scheduler occupancy avg/p95/max
scheduler full cycles
internal ReturnQ occupancy avg/p95/max
internal ReturnQ full cycles
successful read/write issues
successful read/write bytes
verified bandwidth-utilization numerator/denominator or exact derived utilization
```

Kernel deltas are preferred if low-risk.

Parser output:

```text
target_dram.csv
```

### 7. 5K temporal windows

Preserve the existing C7d L2/payload/bank windows. Add channel-level 5K windows for at least:

```text
scheduler occupancy/full
internal ReturnQ occupancy/full
successful DRAM read/write bytes or exact bandwidth utilization
```

Keep host overhead bounded.

### 8. Analyzer/schema cleanup

Update parser/analyzer so labels exactly match producer semantics.

Required analysis-ready outputs include:

```text
Tag-way need/block ratio
Line-MSHR need/full-block ratio
Descriptor need/pool-full-block ratio
Per-address-cap check/block ratio
WAD full/hazard/lifetime
Payload service denial vs capacity denial
Bank true-conflict rate and wait
L1D exact blockers
MissQ / L2->DRAM FIFO
DRAM scheduler causal block + time-weighted occupancy
internal ReturnQ
DRAM->L2 FIFO
actual lower read/write transactions + bytes
bandwidth utilization
```

Do not infer unavailable fields from coarse compatibility counters.

### 9. Formal runner hardening

The formal runner must fail fast before launch unless:

```text
actual Core HEAD == expected Core SHA
actual Framework HEAD == expected Framework SHA
Core worktree clean
Framework source worktree clean
formal overlay/config hashes match the immutable campaign manifest
```

Add explicit expected-SHA support or equivalent immutable pinning.

Use a fresh result root for the final campaign:

```text
docs/ep_l2/target_baseline_results_final_850/
```

Do not reuse older C5c/C6d/C7d result roots.

## Validation and closeout

The exact acceptance gate is in `C7E_ACCEPTANCE_CRITERIA.md`; it is authoritative.

C7e must retain directly reviewable evidence under:

```text
docs/ep_l2/review_packs/C7E_FINAL_READINESS_r1/
```

and publish `codex_handoff/LATEST_REPORT.md` plus the review pack to the permanent coordination branch `hrl/ep-l2-exp-v0`.

If a C7e acceptance item fails, stay within the C7e repair loop defined in `CODEX_TARGET_GOAL.md`; fix the instrumentation/provenance issue, rebuild, rerun the failed gate and any impacted regression, and repeat until every mandatory gate passes.
