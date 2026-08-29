# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This is the authoritative coordination summary for EP-L2. If it conflicts with a newer reviewed closeout, stop and report the conflict instead of guessing.

## 1. Current reviewed source anchors

C6d corrected-bank evidence:

```text
Core      0cde333340792cffed869cbbc7e7dc88667c6b8b
Framework 0a0c0fc3e1ffb6ca346090e59e94d2128e5adc0e
```

C7d final reviewed pair:

```text
Core      88e243e8e421002079adc85b9efae3452c02a828
Framework 2aef9fad48207415a9697f9b891068b42008e0a8
```

Branches:

```text
Core      hrl/ep-l2-c7d-char-v0
Framework hrl/ep-l2-c7d-char-v0
```

C7d is **not** authorized as the final 26-run source pair yet. The next stage is C7e final characterization-readiness closeout, derived from the C7d final pair.

## 2. C6d review result

**PASS. Freeze the C6d bank-arbitration semantics.**

The pre-fix B0-Banked implementation forced every idle-bank payload operation through a mandatory staging/retry cycle. C6d removes that artifact while preserving one operation/bank/cycle and oldest-ready priority for already-pending work.

Retained smoke evidence:

```text
spmv:
  Legacy = 23,453 cycles
  Banked = 23,453 cycles
  true bank conflicts = 0

gemm:
  pre-fix Banked slowdown ≈ 20.7%
  C6d Legacy == Banked
  true bank conflicts = 0

FWT_7_21:
  pre-fix Banked slowdown ≈ 14.5%
  C6d Legacy == Banked
  true bank conflicts = 0

cfd_097k:
  Legacy = 79,555
  Banked = 81,443
  residual slowdown ≈ 2.37%
  true conflict ops/events = 16,166
  bank wait cycles = 16,166
```

These are diagnostic/correctness evidence only after C7d changed source SHAs. They are not final Target-Baseline characterization data.

## 3. Frozen Target Baseline architecture

Per L2 slice unless stated otherwise:

```text
64 L2 slices total
128 B line, 4 x 32 B sectors

Resident Tag:
  64 sets x 16 ways = 1024 entries

Payload:
  1024 resident entries
  128 bypass entries

B0-Legacy:
  separate resident and bypass 1R1W RAMs

B0-Banked:
  1152 entries
  4 x 288 banks
  bank = payload_id % 4
  static 1024 resident + 128 bypass ownership

Line MSHR entries:                 128
Shared persistent request descriptors: 256
Per-address descriptor cap:        32
WAD:                               128 line addresses

ICNT->L2:                          64
L2->DRAM:                          128
DRAM->L2:                          64 / slice
L2->ICNT:                          64
FR-FCFS scheduler:                 128 / channel
DRAM internal ReturnQ:             192 / channel

Primary DRAM clock:                850 MHz

Primary L1D:
  64 KiB
  4 sets x 128 ways x 128 B
  4 banks
  20-cycle latency
  existing QV100 MSHR/MissQ/write semantics retained unless later evidence requires revision
```

No Unified borrowing, RO no-MSHR, replaceable RO pending, TVD functionality, graphics borrowing, or 1GHz primary change belongs in the Target Baseline stage.

## 4. Round-2 diagnostic evidence that remains valid

```text
btree merge sensitivity:
  2 -> 4 -> 8 improves strongly
  8 -> 16 saturates
  => fixed per-MSHR target fragmentation was a real QV100 bottleneck

MissQ 32 -> 64:
  little/no general performance benefit

L2->DRAM 64 -> 128:
  little/no general performance benefit

FR-FCFS scheduler depth:
  vectorAdd strongly benefits from a larger reordering window
  spmv is essentially saturated by 128
  cfd is non-monotonic / negative control
```

Do not interpret FR-FCFS queue-depth sensitivity as pure buffer capacity; it changes scheduling/reordering opportunity.

## 5. C7d review result

**CONDITIONAL PASS as instrumentation development, but NOT READY for the final 26-run.**

C7d successfully added or repaired:

```text
exact LINE_MSHR_FULL / DESCRIPTOR_POOL_FULL / PER_ADDRESS_CAP blocker separation
WAD full vs same-address hazard separation
payload service vs capacity naming
C6d bank logical/attempt/grant/retry/true-conflict/wait semantics
per-bank and operation-class bank counters
kernel bank interval deltas
compact 5K L2/payload/bank windows
additional lower-path counters
parser/analyzer availability discipline
```

The Codex closeout itself correctly reports `NOT_READY_FOR_FINAL_26_RUN` because final-SHA validation evidence and L1 aggregation are incomplete.

## 6. Additional ChatGPT source-review findings after C7d

The following must be resolved in C7e before the expensive final campaign.

### 6.1 L1D is still not actually aggregated into Target telemetry

Core `88e243e8` adds `cache_stats::total_fail_reason()`, but does not wire L1D-only application/kernel snapshots into a Target output schema.

The final campaign therefore cannot yet prove whether L1D MSHR/MissQ/merge/line-allocation/bank pressure is limiting.

### 6.2 C7d DRAM `*_issues` counters are issue-attempt observations, not successful issues

`memory_sub_partition::l2_char_record_dram_issue()` increments `dram_read_issues` / `dram_write_issues` before `can_issue_to_dram()` and before the scheduler-full check has accepted the request.

C7e must separate:

```text
issue/head attempts
actual successful read issues
actual successful write issues
actual issued bytes
```

### 6.3 `c7d_dram_returnq_block` is not the internal DRAM ReturnQ

The producer's `return_block` is based on the per-subpartition `dram_L2_queue_full()` condition. That is the DRAM->L2 slice FIFO / return-path destination, not the channel's internal `dram_t::returnq`.

C7e must measure the two structures separately.

### 6.4 Scheduler occupancy is request-opportunity-weighted, not DRAM-cycle time-weighted

C7d samples scheduler occupancy when an L2->DRAM head is inspected. This is useful conditional telemetry but is not a per-DRAM-cycle average occupancy.

Because Round-2 showed scheduler behavior is important, C7e should add channel-scope DRAM-cycle scheduler occupancy/full-cycle statistics and, if low-cost, 5K channel windows.

### 6.5 Tag/set eligibility denominator is too broad for new-way pressure

C7d `line_alloc_eligible` includes `SECTOR_MISS`, but a sector miss on an already-resident line does not require a new Tag way.

Keep compatibility fields, but add an exact `tag_way_alloc_need/eligible` metric that represents new line/way allocation only.

### 6.6 MSHR/descriptor/cap eligible counters are blocker-reason dependent

When one resource is the selected `full_reason`, other resources needed by the same request may not increment their current `*_eligible` counters.

C7e should add independent need/demand denominators based on request semantics, for example:

```text
line_mshr_need           = needs_new_mshr
descriptor_need          = needs_new_mshr || needs_mshr_merge
per_address_cap_check    = needs_mshr_merge
```

Keep exact blocker reasons separate.

### 6.7 Kernel WAD lifetime fields are currently cumulative

The kernel snapshot prints WAD lifetime statistics directly from cumulative `l2_cache` lifetime totals, rather than launch-to-completion delta state.

Either implement true kernel deltas or explicitly make WAD lifetime application-only; do not label cumulative values as kernel interval data.

### 6.8 Analyzer still lacks final memory-bandwidth output

The current analyzer deliberately returns `NOT_EMITTED_BY_EPL2B0V1` for DRAM bandwidth utilization. Before the final run, either parse exact native DRAM utilization with verified semantics or add explicit channel-scope Target output.

### 6.9 5K windows do not include scheduler occupancy

Current 5K records contain line MSHR, descriptor, WAD, resident payload, MissQ, L2->DRAM FIFO, and bank metrics, but not scheduler occupancy. Add it if the channel-level collector can do so without material host overhead.

### 6.10 Final runner captures SHAs but does not fail-fast on expected SHAs

The final runner records current Framework/Core HEADs, but a user can still launch from the wrong revision.

C7e should add explicit expected-SHA and clean-worktree checks before a formal campaign starts.

## 7. C7e objective

C7e is the **last instrumentation/readiness stage before the final 26-run**.

It must remain timing-neutral and must not change Target architecture behavior.

After C7e passes, freeze one final source pair and run exactly one clean:

```text
13 workloads x {B0-Legacy, B0-Banked} @850 MHz
= 26 formal runs
```

The campaign must be sufficient to analyze:

```text
Tag/set new-way pressure
Line MSHR pressure
Global descriptor pool pressure
Per-address cap pressure
WAD capacity and ordering hazards
Payload role/service pressure
real bank contention
L1D pressure
MissQ and L2->DRAM FIFO pressure
DRAM scheduler pressure
internal ReturnQ pressure
DRAM->L2 return-path pressure
actual lower traffic / bytes / bandwidth utilization
sustained vs bursty behavior
Legacy vs Banked attribution
```

## 8. Opportunity study remains separate

The final 26-run characterizes the Target Baseline. It does not replace the later timing-neutral opportunity stage.

After Target-Baseline freeze:

```text
RO oracle + RO shadow
TVD shadow
Payload-role complementarity shadow
kernel/epoch snapshots
```

Opportunity runs should primarily use B0-Banked because the proposed Unified design uses the same 4-bank physical organization.

## 9. Current execution order

```text
C6d PASS / frozen
        |
C7d CONDITIONAL PASS
        |
        v
C7e final characterization-readiness instrumentation
        |
        v
final-SHA build/regression/timing-neutrality/host-overhead closeout
        |
        v
ChatGPT review
        |
        v
one clean final 26-run @850 MHz
        |
        v
Target-Baseline bottleneck analysis and freeze
        |
        v
small 1GHz headroom subset if justified
        |
        v
RO / TVD / complementarity opportunity branch
```
