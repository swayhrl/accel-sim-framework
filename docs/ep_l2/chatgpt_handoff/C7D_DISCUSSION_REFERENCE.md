# C7d Discussion Reference — Why the Final 26-run Needs a Telemetry Completeness Pass

Updated: 2026-08-30

This file preserves the user question and the reasoning that motivated C7d.

## User question

> 正式 26-run 可以一轮采集完数据，用于我们分析真正的瓶颈和 EP-L2 opportunity吗？先分析分析，确保该采集的数据目前的代码实现下均能采集到，结合github仓库实际代码检查。
>
> Translation:
>
> Can the formal 26-run collect all data in one pass for analyzing the real bottlenecks and EP-L2 opportunity? First analyze this carefully and make sure all required data can actually be collected by the current implementation, based on the real GitHub source.

## Conclusion

Not with the pre-C7d instrumentation.

The current implementation already measures many useful Target-Baseline occupancies and corrected C6c bank metrics, but several bottleneck reasons are merged or mislabeled, some L1/lower-path data is incomplete, kernel bank counters need true interval-delta semantics, and there are no compact Target-Baseline temporal windows.

Separately, RO/TVD/Unified opportunity requires dedicated timing-neutral shadow state and cannot be reconstructed from aggregate B0 statistics.

Recommended flow:

```text
C7d instrumentation completeness
        ->
one clean 13 x 2 @850 MHz Target-Baseline campaign
        ->
freeze/analyze Target Baseline
        ->
separate opportunity branch with RO/TVD/complementarity shadows
```

## What current EPL2B0V1 already measures

At C6c Core anchor:

```text
0cde333340792cffed869cbbc7e7dc88667c6b8b
```

the producer already emits per-slice:

```text
line MSHR avg/p95/max
descriptor avg/p95/max
WAD avg/p95/max
resident payload avg/p95/max
bypass payload avg/p95/max
MissQ avg/max
L2->DRAM FIFO avg/max

coarse block_descriptor / block_wad / block_payload / block_bank / block_l1 / block_lower

C6c bank:
  logical ops
  attempts
  grants
  retry attempts
  true-conflict ops/events
  wait cycles

application cumulative snapshots
kernel completion records
terminal invariants
```

The Framework parser already creates:

```text
target_summary.csv
target_slice.csv
target_kernel.csv
target_bank.csv
manifest.json
```

This is a good foundation.

## MSHR / descriptor ambiguity

The Core already has exact block reasons:

```text
EP_L2_BLOCK_LINE_MSHR_FULL
EP_L2_BLOCK_DESCRIPTOR_POOL_FULL
EP_L2_BLOCK_PER_ADDRESS_CAP
```

but pre-C7d `EPL2B0V1` aggregates these into one coarse `block_descriptor` path.

That is scientifically insufficient because RO no-MSHR can save address-indexed MSHR state while still consuming request descriptors. The final Target-Baseline analysis must know which resource actually blocks.

## WAD ambiguity

The production cache already owns exact counters for:

```text
WAD capacity-full block
same-address read waiting behind outstanding writeback
```

but the coarse Target collector previously inferred WAD blocking from nonzero WAD occupancy during other stalls.

C7d must separate:

```text
WAD_FULL
same-address hazard events
same-address wait cycles
WAD lifetime
```

## Lower-path ambiguity

Pre-C7d `block_lower` corresponds to a lower-read request encountering the per-slice L2->DRAM FIFO full condition. It is not equivalent to FR-FCFS scheduler blocking.

Round-2 already showed why this matters:

```text
MissQ capacity increase -> little general benefit
L2->DRAM capacity increase -> little general benefit
FR-FCFS scheduling-window increase -> workload-dependent performance effects
```

So the final Target-Baseline output must distinguish:

```text
MissQ
L2->DRAM FIFO
DRAM scheduler
ReturnQ
DRAM->L2
DRAM bandwidth
```

## L1 gap

The pre-C7d accumulator contains an `l1_block` field, but source audit did not establish complete production wiring sufficient to interpret `l1_block == 0` as “L1 is not a bottleneck.”

Native cache statistics already expose several reservation-failure categories. C7d should reuse exact native fields where trustworthy and add lightweight target-specific counters only where needed.

## C6c bank analyzer semantics

The meaningful primary bank conflict rate after C6c is:

```text
bank_true_conflict_ops / bank_logical_ops
```

not failed-attempts/all-attempts.

The analyzer must consume `bank_wait_cycles` and the corrected C6c fields.

## Kernel bank-delta issue

The kernel snapshot path computes an accumulator delta for normal EPL2B0V1 stats, but bank counters were read from cumulative l2_cache counters. C7d must make kernel bank data true interval deltas.

## Why compact 5K windows matter

Application avg/p95/max cannot reliably distinguish sustained pressure from brief bursts.

Round-1 showed this distinction matters. C7d should add compact 5K windows for only the key Target resources, without recreating the expensive full L2CHARV1 collector.

## What the final 26-run should answer after C7d

```text
Tag/set bottleneck?
128 line MSHRs full?
256 descriptors full?
32/address cap active?
WAD capacity/hazard?
Payload service/capacity?
Real bank conflict?
L1 bottleneck?
MissQ vs L2->DRAM vs scheduler vs ReturnQ vs DRAM bandwidth?
Sustained vs bursty pressure?
Legacy -> Banked attribution closed?
```

## Why opportunity still needs a separate shadow stage

### RO no-MSHR

Required opportunity data includes:

```text
RO coverage
same-line arrivals before fill
waiter count
potential detach
duplicate lower reads/bytes
read amplification
released-tag cycles
MSHR relief
descriptor pressure increase
payload pressure increase
lower-traffic increase
```

This requires oracle read-only classification plus per-address/per-transaction shadow state.

### TVD

Required shadow state includes:

```text
victim block address
clean/dirty
eviction cycle
WB state
reuse before/during/after WB
reuse age/time
potential avoided lower reads/bytes
metadata-only vs payload-only miss
promotion/wait opportunity
```

The baseline WAD set does not contain this reuse history.

### Unified payload complementarity

Required role-over-time state includes:

```text
resident
normal fill
RO fill
bypass
dirty-WB retained
TVD
FREE
```

plus:

```text
pairwise temporal correlation
sum-of-peaks
peak-of-sum
borrow demand
reclaim demand
```

Static B0 resident/bypass occupancy is not enough to derive this.

## Final research workflow

```text
C6c correctness/performance smoke
        +
C7d instrumentation completeness
        |
        v
C7d review/freeze
        |
        v
one clean 26-run @850 MHz
        |
        v
Target-Baseline bottleneck analysis
        |
        v
optional small 1 GHz subset
        |
        v
opportunity branch
        |
        +-- RO oracle/shadow
        +-- TVD shadow
        +-- payload complementarity
        |
        v
mechanism gates
        |
        v
only then implement justified mechanisms
```

Keep these claims separate:

```text
Target Baseline characterization
!= opportunity upper-bound/shadow study
!= functional mechanism performance evaluation
```
