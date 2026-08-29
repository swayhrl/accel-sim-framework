# EP-L2 C7e Discussion Reference

Updated: 2026-08-30

This file records the ChatGPT source review that followed the C6d/C7d Codex closeout. It explains why the final 26-run remains blocked and why C7e is necessary.

## 1. Review entry point inspected

Codex published the C6d/C7d closeout on:

```text
Framework branch: hrl/ep-l2-c7d-char-v0
Core branch:      hrl/ep-l2-c7d-char-v0
```

Reported final pair:

```text
Core      88e243e8e421002079adc85b9efae3452c02a828
Framework 2aef9fad48207415a9697f9b891068b42008e0a8
```

Codex's own formal readiness report concluded:

```text
C6d correctness: YES
C7d telemetry complete: NO
final-SHA timing-neutrality evidence: missing
final recommendation: NOT_READY_FOR_FINAL_26_RUN
```

ChatGPT agrees with that decision and found additional producer-level issues described below.

---

# 2. C6d is accepted

C6d successfully removed the artificial B0-Banked mandatory staging cycle.

Retained smoke comparison:

```text
spmv:
  pre-fix Banked slower
  C6d Legacy == Banked
  true contention = 0

gemm:
  pre-fix Banked ≈20.7% slower
  C6d Legacy == Banked
  true contention = 0

FWT_7_21:
  pre-fix Banked ≈14.5% slower
  C6d Legacy == Banked
  true contention = 0

cfd_097k:
  residual Banked slowdown ≈2.37%
  true conflict ops/events = 16,166
  bank wait cycles = 16,166
```

Therefore the C6d arbitration semantics should be frozen. C7e must not modify them.

---

# 3. C7d improvements that should be preserved

C7d correctly introduced or improved:

```text
independent exact LINE_MSHR_FULL / DESCRIPTOR_POOL_FULL / PER_ADDRESS_CAP fields
WAD full / hazard separation
resident dirty / valid / pending role observations
payload service-vs-capacity naming
C6d bank logical/attempt/grant/retry/true-conflict/wait fields
per-bank and operation-class bank counters
kernel bank interval deltas
compact 5K windows for several L2 resources
lower-path fields
parser/analyzer availability discipline
```

The final design should preserve the principle:

> Never infer a specific hardware resource bottleneck from a coarse compatibility counter when the producer did not actually measure that resource.

---

# 4. L1D is still missing from final Target telemetry

Core commit `88e243e8` adds only:

```text
cache_stats::total_fail_reason(reason)
```

which sums one native fail reason across streams/access types inside a `cache_stats` object.

No final C7d producer actually creates an L1D-only Target application/kernel record from it.

Native L1D fail reasons do exist, including:

```text
LINE_ALLOC_FAIL
MISS_QUEUE_FULL
MSHR_ENRTY_FAIL
MSHR_MERGE_ENRTY_FAIL
MSHR_RW_PENDING
```

and the LD/ST path also has a real L1D bank/latency-queue conflict event (`gpgpu_n_l1cache_bkconflict`).

However, existing generic core-cache aggregation combines L1I/L1D/L1C/L1T, so the final Target-Baseline analysis must not use that mixed aggregate as L1D pressure.

C7e should expose L1D-only GPU-scope application and kernel deltas, preferably under a separate schema (`EPL2L1V1`) rather than duplicating one GPU-global value into every L2 slice.

---

# 5. C7d DRAM `read_issues/write_issues` are not successful issues

In final C7d, `memory_partition_unit::dram_cycle()` computes for an L2->DRAM head:

```text
return-path block
credit block
scheduler full
scheduler occupancy
```

then calls:

```text
memory_sub_partition::l2_char_record_dram_issue(...)
```

**before** the production code executes:

```text
if (!can_issue_to_dram(...)) continue;
if (m_dram->full(...)) continue;
```

Inside `l2_char_record_dram_issue()` C7d increments:

```text
dram_issue_eligible
dram_read_issues / dram_write_issues
```

regardless of whether the request subsequently issues successfully.

Therefore the current `*_issues` fields are issue-head attempts/observations, not completed issue events.

This matters because the final baseline analysis needs actual lower traffic and because future RO shadow work will compare duplicate lower traffic against a trustworthy baseline.

C7e must separately count successful issue transactions and bytes at the exact production point after all gates pass and the request leaves the L2->DRAM arbitration path.

---

# 6. C7d `dram_returnq_block` names the wrong structure

In the issue path C7d computes:

```text
return_block = needs_return && m_sub_partition[spid]->dram_L2_queue_full()
```

`m_dram_L2_queue` is the **per-slice DRAM->L2 FIFO**.

It is not the internal channel `dram_t::returnq` configured by:

```text
-gpgpu_dram_return_queue_size 192
```

The architecture and prior source audit explicitly treat these as distinct resources:

```text
DRAM internal ReturnQ: per channel
DRAM->L2 FIFO:         per slice
```

C7e must measure/name them separately.

---

# 7. Scheduler occupancy is conditional, not time-weighted

C7d adds scheduler occupancy to the per-slice accumulator only inside `l2_char_record_dram_issue()`.

That function runs when an L2->DRAM head is inspected. Hence its average is roughly:

```text
scheduler occupancy seen by issue opportunities
```

not:

```text
time-average scheduler occupancy over DRAM cycles
```

This distinction matters because Round-2 showed FR-FCFS scheduling-window behavior is a major workload-dependent factor.

C7e should preserve the conditional metric if useful but add per-channel DRAM-cycle occupancy/full-cycle telemetry.

A separate channel-scope schema is preferred to avoid duplicating a shared channel quantity into two L2 subpartitions and accidentally summing it twice.

---

# 8. Current 5K windows omit scheduler/ReturnQ/BW temporal pressure

C7d 5K windows currently emit:

```text
line MSHR avg
descriptor avg
WAD avg
resident payload avg
MissQ avg
L2->DRAM FIFO avg
bank logical ops
bank true-conflict ops
bank wait cycles
```

They do not emit channel scheduler occupancy, internal ReturnQ occupancy, or memory-bandwidth utilization.

Because the final campaign should distinguish sustained vs bursty lower-memory pressure, C7e should add channel-level 5K memory windows if the host cost remains bounded.

---

# 9. Tag-way eligibility needs a narrower denominator

C7d currently defines a `line_alloc` eligibility condition containing:

```text
MISS
SECTOR_MISS
all-reserved
WAD-full
```

For a sector cache, `SECTOR_MISS` can occur when the 128B line is already resident and only another 32B sector must be allocated/fetched.

That does not require a new Tag way.

Therefore `line_alloc_eligible` is too broad if used as the denominator for Tag/set-way pressure.

C7e should add a separately named exact new-line/new-way demand field and use it for Tag-way blocking ratios.

---

# 10. MSHR/descriptor eligible denominators depend on blocker priority

Current C7d logic increments one `*_eligible` field based on the selected `mshr_table::full_reason()` when a resource is full.

This means, for example, a request that needs both a new MSHR and a descriptor may only contribute to the descriptor denominator if descriptor-full is the selected reason, even though it semantically needs both resources.

For cross-resource analysis, the cleaner contract is:

```text
need/demand counters are independent
blocker reason remains exact and priority-selected
```

Recommended definitions:

```text
line_mshr_need        = needs_new_mshr
descriptor_need       = needs_new_mshr || needs_mshr_merge
per_address_cap_check = needs_mshr_merge
```

Then exact blocker events remain:

```text
LINE_MSHR_FULL
DESCRIPTOR_POOL_FULL
PER_ADDRESS_CAP
```

This allows the final paper analysis to distinguish demand frequency from the actual blocking resource.

---

# 11. Kernel WAD lifetime is currently cumulative

Kernel `EPL2B0V1` snapshots correctly delta most accumulator fields.

However WAD lifetime avg/p95/max are printed directly from cumulative `l2_cache` lifetime totals.

Therefore a later kernel can inherit lifetime samples from earlier kernels.

C7e should either implement true kernel lifetime deltas or explicitly mark lifetime as application-only.

---

# 12. Framework analyzer still cannot report DRAM bandwidth

The final C7d analyzer intentionally emits:

```text
dram_bandwidth_util = NOT_EMITTED_BY_EPL2B0V1
```

This is safer than guessing, but it means the final 26-run still cannot directly produce the memory-ceiling table required by the research plan.

C7e should either expose exact verified channel utilization in a Target schema or parse the native DRAM metric with a documented numerator/denominator contract.

Actual transaction bytes should also be recorded at successful issue time rather than inferred from a fixed request size.

---

# 13. Runner provenance is recorded but not actually pinned

The C7d Framework runner supports selecting a separate Core worktree via `EP_L2_CORE` and records the checked-out Core/Framework HEADs in the campaign manifest.

However it does not fail before the campaign if the actual HEAD differs from the reviewed expected SHA.

For an expensive formal campaign, this is not strong enough.

C7e should require expected Core/Framework SHAs and clean source worktrees before any run starts.

---

# 14. Final-SHA validation evidence is mandatory

The C7d review pack does not retain final-source evidence for:

```text
full Release build
combined C3-C7/C6d regression
instrumentation OFF vs ON exact timing neutrality
host overhead
```

This is a reproducibility/readiness issue even if no correctness bug is currently known.

C7e must rerun these checks on the exact final C7e source pair and retain compact evidence in the review pack.

---

# 15. Why C7e should be the last source-changing baseline stage

The remaining changes are measurement/provenance corrections, not architecture changes.

After C7e the desired state is:

```text
C6d bank semantics frozen
Tag/MSHR/descriptor/WAD/payload telemetry exact
L1D pressure visible
lower hierarchy structurally separated
actual traffic + bytes + BW visible
channel scheduler/ReturnQ pressure visible
5K temporal pressure sufficient
runner SHA-pinned
final-source timing neutrality proven
```

At that point the next expensive run should be exactly one clean:

```text
13 workloads x B0-Legacy/B0-Banked @850 MHz
```

and should not need to be repeated for missing Target-Baseline telemetry.

Opportunity instrumentation remains a separate post-baseline stage because RO/TVD/Unified opportunity requires shadow state that cannot be reconstructed from B0 aggregates.
