# EP-L2 Motivation Figures Plan

Status: **canonical motivation-figure specification**

This document freezes the definitions for the two primary motivation figures used to explain why EP-L2 should improve L2 structural efficiency rather than merely enlarge cache capacity.

## 1. Research questions

The two figures answer two different questions.

### Figure 1 — reuse structure

Does an application's L2-level reuse tend to return within a short bounded distance, or is reuse predominantly long-distance / effectively streaming?

This figure supports deciding whether a victim-like retained-payload mechanism can plausibly capture useful short-term reuse versus whether the more important problem is concurrent miss/pending-state capacity and latency hiding.

### Figure 2 — structural blocking composition

When an L2 demand miss cannot be admitted, which transient resource is the primary structural limiter?

The primary paper-facing categories are:

```text
Set / Associativity
MSHR / Metadata
MissQ / LowerQ
WB-path
```

The WB-path category uses an explicitly shadowed finite dirty-writeback data buffer with reference capacity 8. Capacities 4 and 16 are collected in the same execution for sensitivity.

---

## 2. Figure 1: L2 reuse-distance distribution

### 2.1 Reference stream

The primary stream is the **frontend L2 demand line-reference stream**.

One reference is one upper-level demand request that performs an L2 lookup, normalized to the 128-B L2 block address.

The primary stream excludes:

- L2-generated writeback packets;
- DRAM fills/returns;
- internal retry/replay bookkeeping that does not represent a new frontend demand reference;
- instrumentation-only synthetic traffic.

The implementation must source-audit exact included/excluded `mem_access_type` / request classes before collecting formal data.

### 2.2 Kernel/epoch scope

Primary reuse state resets at the existing kernel/epoch boundary. Application-level bars are formed by aggregating reuse instances across the application's kernels/epochs.

A supplemental application-global stream may be emitted, but the paper-facing primary figure uses within-kernel/epoch reuse so unrelated kernel working sets are not silently blended.

### 2.3 Reuse-distance definition

For two consecutive references to the same 128-B block within one kernel/epoch, define reuse distance as:

> the number of **distinct 128-B L2 block addresses** referenced between those two references in the same L2-slice demand stream.

This is stack/reuse distance, not elapsed cycles and not raw intervening-reference count.

The profiler only needs exact rank through 1024 distinct blocks. Anything larger is classified as `>1K`.

Required bins:

```text
<=8
9-16
17-32
33-64
65-128
129-256
257-512
513-1024
>1024
```

The nine plotted fractions are normalized over **reuse instances only** and therefore sum to 1.0 for every workload with at least one reuse instance.

### 2.4 Required companion coverage metrics

The stacked bar alone is insufficient. Also emit:

```text
eligible_demand_references
reuse_instances
reuse_instance_fraction = reuse_instances / eligible_demand_references
unique_lines
unique_lines_reused_at_least_once
one_touch_unique_lines
line_reuse_coverage = unique_lines_reused_at_least_once / unique_lines
one_touch_line_fraction = one_touch_unique_lines / unique_lines
```

These metrics prevent a workload with very little reuse from appearing "cache friendly" merely because its small reused subset is short-distance.

### 2.5 Post-eviction reuse supplement

In the same run, record a supplemental real-eviction stream:

```text
block address
eviction demand-sequence index
eviction cycle
next frontend demand re-reference, if any
```

Emit post-eviction reuse-distance/time histograms and:

```text
post_eviction_referenced_fraction
post_eviction_within_8/16/32/64/128/256/512/1K_fraction
```

This is supplemental evidence for victim-like opportunity. It must not change real cache hit/miss behavior.

---

## 3. Figure 2: L2 miss-admission structural blocking composition

### 3.1 Denominator

Figure 2 is restricted to **frontend demand-miss admission blocking**.

It does not attempt to decompose every possible L2 stall (for example payload-bank service on hits or response-network backpressure).

For each capacity scenario, define:

```text
eligible_miss_admission_cycles
projected_blocked_miss_admission_cycles
```

The plotted fractions are computed only over the projected blocked miss-admission cycles and must sum to 1.0.

### 3.2 Four primary classes

#### A. Set / Associativity

Includes the first production-visible admission failure caused by resident tag/set/way allocation state, for example all-reserved / no allocatable resident entry.

#### B. MSHR / Metadata

Includes the first production-visible failure caused by transient request metadata capacity, including as applicable:

```text
Line-MSHR entry full
per-address requester/chain cap
persistent descriptor-pool full
MSHR ordering/RW-pending admission restrictions
```

The plot legend may say `MSHR`, but the caption/table must state that the category is MSHR/metadata concurrency rather than only the 128 line-entry array.

#### C. MissQ / LowerQ

Includes the first production-visible failure caused by the short lower-issue/request path capacity required to launch the miss, including the actual target-model MissQ/lower-queue admission check defined by the source audit.

The source map must explicitly distinguish this from the persistent requester descriptor pool.

#### D. WB-path

Includes writeback-path constraints required to commit a dirty-victim miss:

```text
mandatory WAD/order-hazard restriction
mandatory WAD capacity restriction
shadow finite WBUF capacity restriction
```

The paper-facing label is `WB-path` or `WBUF(proxy)`, not an assertion that the existing simulator already contained a real dedicated hardware WBUF.

### 3.3 Exclusive primary classification

For each capacity scenario and each eligible miss-admission cycle, assign **at most one** primary class.

The classifier must follow the source-audited production admission order and select the first resource that prevents the request from committing.

Do not sum independent event counters to form the stacked bar.

For every capacity C:

```text
SET_ASSOC_C
+
MSHR_META_C
+
MISSQ_LOWER_C
+
WB_PATH_C
+
OTHER_C
=
projected_blocked_miss_admission_cycles_C
```

`OTHER_C` is diagnostic only. The four-category paper figure is allowed only if `OTHER_C` is <=2% for every plotted workload. Otherwise the main figure must retain an `Other` segment or return for review.

---

## 4. Shadow WBUF definition

### 4.1 Physical interpretation

The shadow WBUF is a finite **Dirty Writeback Data Buffer** holding the 128-B dirty-line data / WB packet after victim data readout and WB-packet creation, while that packet waits for the lower path to accept it.

It is not the WAD.

```text
WBUF = dirty data / WB packet staging
WAD  = line-address ordering and WB hazard tracking
```

### 4.2 Allocation event

Allocate one shadow WBUF entry when a real dirty victim has completed the required payload readout and the simulator creates the corresponding lower writeback transaction/packet.

The exact production event must be source-audited and recorded in the implementation map.

### 4.3 Release event — frozen

> **Release the WBUF slot when that WB is successfully accepted into the per-slice lower path / L2->DRAM interface.**

Do **not** retain the WBUF entry until final `set_done()` / writeback completion.

WAD may remain live after WBUF release according to its independent ordering lifetime.

### 4.4 Capacities collected in one run

One simulator execution simultaneously evaluates:

```text
WBUF = 4
WBUF = 8
WBUF = 16
```

These are timing-neutral trace-projected shadow capacities, not three independently timing-perturbed architectures.

### 4.5 Shadow semantics

The real simulator request stream is unchanged. Maintain the exact set/count of real WB packets whose lifetime is:

```text
WB packet creation -> real lower-path acceptance
```

For C in `{4,8,16}`, evaluate whether the currently observed dirty-victim admission would have encountered `active_wb_packets >= C` at the WBUF admission point.

Required labels use `shadow`, `trace_projected`, or `would_block` terminology.

Do not call shadow C=4/8/16 results end-to-end performance results.

### 4.6 Required WBUF metrics

For every capacity C:

```text
wbuf_C_alloc_opportunities
wbuf_C_trace_projected_would_block_events
wbuf_C_trace_projected_would_block_cycles
wbuf_C_occ_avg
wbuf_C_occ_p50
wbuf_C_occ_p95
wbuf_C_occ_max
wbuf_C_full_cycle_fraction
```

Also emit capacity-independent real WB staging lifetime:

```text
wb_packet_creation_to_lower_accept_cycles_avg
p50
p95
max
wb_packets_created
wb_packets_lower_accepted
```

---

## 5. Paper-facing figures

### Figure 1

`L2 Reuse-Distance Distribution`

- one stacked bar / workload;
- nine distance bins;
- each bar sums to 1.0;
- companion CSV/table carries reuse coverage and one-touch fraction.

### Figure 2

`L2 Miss-Admission Structural Blocking Breakdown`

Primary version uses:

```text
WBUF reference capacity = 8
```

Segments:

```text
Set/Assoc
MSHR/Metadata
MissQ/LowerQ
WB-path
```

Each bar sums to 1.0 over projected blocked miss-admission cycles.

### WBUF sensitivity supplement

The same run must also generate WBUF=4 and WBUF=16 breakdowns plus a compact sensitivity table/plot.

Do not run the workloads three times merely to obtain the 4/8/16 motivation comparison.

---

## 6. Workload plan

Correctness/pilot set first:

```text
vectorAdd_4M
convolutionSeparable
spmv
sad
```

After all correctness/timing-neutrality gates pass, launch the broad motivation set in parallel where host resources permit:

```text
scan
vectorAdd_4M
convolutionSeparable
spmv
FWT_7_21
cfd_097k
dwt2d
sad
btree
gemm
```

The remaining calibrated-baseline workloads may be added if cheap, but the two primary motivation figures must not wait for low-information workloads once the representative set is complete.

---

## 7. Interpretation boundary

Figure 1 supports statements about short/long L2 reuse structure. It does not by itself prove a victim mechanism improves performance.

Figure 2 supports statements about structural miss-admission pressure under an explicitly defined WBUF shadow capacity. It does not by itself prove that a real WBUF of a given size changes application cycles by the same proportion.

Performance claims require later functional/sensitivity experiments.