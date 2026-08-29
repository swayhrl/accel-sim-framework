# EP-L2 C7e Acceptance Criteria

This file is the authoritative self-gating contract for C7e.

Codex is authorized to iterate within C7e until **all mandatory gates are PASS**. A failed mandatory gate is not a reason to stop and wait for ChatGPT unless fixing it would cross a hard boundary listed below.

## A. Functional-scope invariance — mandatory

PASS only if source review and regression evidence show C7e changed observation/provenance only.

No changes are allowed to:

```text
L2 geometry/replacement
MSHR/descriptor capacities/lifetimes
WAD functional behavior
payload capacity/ownership
C6d bank arbitration semantics/timing
L1 configuration
queue capacities
DRAM scheduler/timing parameters
850 MHz primary config
```

Any required change to one of these is a **HARD STOP** requiring ChatGPT review.

## B. Tag / MSHR / descriptor exactness — mandatory

PASS only if directed tests and producer source prove:

```text
SECTOR_MISS on existing line does not increment c7e_tag_way_alloc_need
new-line allocation does increment c7e_tag_way_alloc_need
all-reserved/no-replaceable-way increments c7e_tag_way_alloc_block

new unique line request increments c7e_line_mshr_need
all persistent waiters/requesters increment c7e_descriptor_need exactly once
existing-line merge increments c7e_per_address_cap_check

LINE_MSHR_FULL
DESCRIPTOR_POOL_FULL
PER_ADDRESS_CAP
```

remain separately identifiable blockers.

For a synthetic case where multiple resources are simultaneously near/full, demand denominators must remain semantic/independent even though the final blocker reason may follow production priority.

## C. WAD semantics — mandatory

PASS only if:

```text
WAD_FULL is counted only on real WAD-capacity denial
same-address hazard event is distinct from WAD_FULL
hazard wait cycles count actual repeated wait cycles
WAD lifetime ends at real writeback completion
```

Kernel WAD lifetime must either be true launch-to-completion delta or explicitly unavailable. Cumulative application lifetime must never be labeled as a kernel delta.

## D. Payload / bank semantics — mandatory

C6d semantics are frozen.

PASS only if:

```text
payload service-port denial != payload capacity denial
bank_true_conflict_ops / bank_logical_ops is the primary conflict rate
idle-bank isolated op incurs no artificial staging/retry
per-bank totals sum to aggregate totals
operation-class totals are internally consistent with logical payload ops, subject to documented classes
kernel bank records are true interval deltas
```

No regression of C6d zero-contention behavior is allowed.

## E. L1D characterization — mandatory

PASS only if a GPU-scope **L1D-only** application record exists and is parser-visible for:

```text
accesses
misses
LINE_ALLOC_FAIL
MISS_QUEUE_FULL
MSHR_ENTRY_FAIL
MSHR_MERGE_FAIL
MSHR_RW_PENDING
L1D bank/latency-queue conflict
```

It must not mix L1I/L1C/L1T into the L1D values.

Sequential multi-kernel evidence must prove kernel records are launch-to-completion deltas. If overlapping kernels occur, overlap must be explicitly marked and described as shared-resource interval data.

A zero value is valid evidence only if the producer is actually wired and the test/sample demonstrates the field exists.

## F. DRAM/lower-path characterization — mandatory

PASS only if exact telemetry distinguishes:

```text
L2->DRAM FIFO full/block
DRAM issue/head attempt
DRAM successful read issue
DRAM successful write/WB issue
successful read bytes
successful write bytes
scheduler full observed
scheduler causal block
scheduler time-weighted occupancy
DRAM internal ReturnQ occupancy/full
per-slice DRAM->L2 FIFO occupancy/full/block
credit blocking
```

Directed tests must prove an attempted issue that is denied by scheduler/credit/return-path pressure does not increment successful-issue counters.

Internal ReturnQ and per-slice DRAM->L2 FIFO must have distinct source points and distinct output fields.

## G. DRAM bandwidth — mandatory

PASS only if the final analysis can derive a verified utilization using explicit producer numerator/denominator or a documented exact formula based on successful transferred bytes and the configured channel bandwidth/time base.

The output must no longer be `NOT_EMITTED_BY_EPL2B0V1` for the required final application-level DRAM bandwidth metric.

## H. 5K temporal coverage — mandatory

PASS only if a natural final-SHA workload produces non-empty window data that includes:

```text
line MSHR
descriptor
WAD
resident payload
MissQ
L2->DRAM FIFO
bank logical/conflict/wait
scheduler occupancy/full
internal ReturnQ occupancy/full
successful DRAM bytes or bandwidth utilization
```

Channel-level windows must not be duplicated per subpartition and summed as independent channels.

## I. Parser / analyzer alignment — mandatory

PASS only if parser/analyzer regressions prove:

```text
producer field names == parsed field meanings == analyzer labels
```

The analyzer must not reinterpret compatibility fields as exact blockers.

Required primary ratios include:

```text
Tag-way block / Tag-way need
Line-MSHR-full block / Line-MSHR need
Descriptor-pool-full block / Descriptor need
Per-address-cap block / Per-address-cap checks
Bank true-conflict ops / bank logical ops
```

Wait-cycle fields must not be labeled as events, and occupancy averages must not be labeled as events.

## J. Exact final-SHA build/regression evidence — mandatory

On the final C7e source pair retain compact evidence for:

```text
full Release build
C3-C7 + C6d + C7e directed/integrated regressions
parser regression
analyzer regression
Tag/MSHR/descriptor tests
WAD tests
L1D tests
DRAM attempt/success tests
ReturnQ-vs-DRAM->L2 tests
channel occupancy/window tests
kernel-delta tests
terminal invariants
git diff --check
clean source worktrees
```

Source-level confidence without retained final-SHA execution evidence is NOT sufficient.

## K. Instrumentation timing neutrality — mandatory

Using the **exact final C7e source pair**, run one natural short/medium workload with instrumentation OFF and ON.

PASS requires exact equality of at least:

```text
gpu_tot_sim_cycle
terminal instruction count
L2 accesses
L2 misses
actual successful DRAM read transactions
actual successful DRAM write transactions
```

and any other selected functional/timing counters used by the project.

Only telemetry text/output volume and host wall time may differ.

## L. Host overhead — mandatory measurement, not a correctness threshold

Measure the same natural workload OFF vs ON.

Preferred:

```text
3 OFF + 3 ON repetitions
median wall time
same host/load conditions as practical
```

If repeated measurement is impractical, one OFF/ON pair is acceptable only if the limitation and host-load context are documented.

No arbitrary overhead percentage is a PASS/FAIL correctness threshold; the result is used to decide formal campaign concurrency.

## M. Natural final-SHA sample — mandatory

Retain at least:

```text
one natural final-SHA run with non-empty 5K windows
one sequential multi-kernel final-SHA run proving kernel delta semantics
```

Parsed artifacts must include all applicable:

```text
target_summary.csv
target_slice.csv
target_kernel.csv
target_bank.csv
target_window.csv
target_l1.csv
target_dram.csv
manifest.json
```

## N. Formal runner fail-fast — mandatory

PASS only if the runner demonstrably refuses to start when any of the following is wrong:

```text
Core SHA
Framework SHA
Core worktree cleanliness
Framework source worktree cleanliness
formal config/overlay hash
```

A positive preflight must also show the exact approved pair launches normally.

## O. Final readiness result

C7e is accepted only if every mandatory section A-N is PASS and the review pack ends with:

```text
READY_FOR_FINAL_26_RUN
```

No `CONDITIONAL PASS` is sufficient for automatic transition into the expensive campaign.

## Repair loop

If any mandatory item fails:

1. classify the failure;
2. fix only the minimum instrumentation/parser/runner/provenance issue;
3. make a scoped commit;
4. rerun the failed gate;
5. rerun any tests whose semantics could be impacted;
6. update the closeout evidence;
7. repeat until A-N are all PASS.

Do not accumulate known failures and launch the formal campaign anyway.

## Hard-stop conditions

Stop and request ChatGPT review only if resolving a gate appears to require:

```text
changing frozen architectural/resource semantics
changing benchmark/trace inputs
changing the frozen 850 MHz target configuration
weakening/removing an invariant to make a test pass
accepting unexplained timing differences between instrumentation OFF/ON
silently changing the meaning of an existing formal metric
```
