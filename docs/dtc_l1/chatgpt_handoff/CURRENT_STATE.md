# DTC-L1 / ISCAS 2027 Current State

Last coordination update: 2026-09-24

Status: **SIMULATOR MAINLINE NEAR-CLOSED; BUFFERING × MEMORY-SERVICE INTERACTION STUDY AUTHORIZED**

## 1. Current paper objective

The final objective is a high-quality ISCAS 2027 paper around Decoupled-Tag Cache (DTC), not an open-ended simulator campaign.

The paper should establish:

1. DTC decouples logical Tag visibility / miss state from physical data-line lifetime.
2. IO uses ordered completion/release; OO uses explicit dependency/reference-state tracking.
3. The main performance gain is real under a fixed 64-SM trace-driven platform.
4. The gain is not explained solely by extra physical storage, transaction granularity, or total lower traffic.
5. Higher L1-side concurrency can create workload-specific downstream oversubscription.
6. The final simulator question is whether the lost performance in difficult workloads reflects only finite buffering, deeper memory-service limits, or an interaction between the two.

## 2. Frozen / closed evidence — do not redo

Read-only scientific authorities include:

- FAST64 primary Base / IO / OO evidence.
- Lane-E frozen mechanism-analysis package.
- accepted 80-KiB conventional-cache capacity control.
- dissertation/source granularity audit.
- accepted same-Core sector-vs-whole-line fairness controls.
- SG4A bounded logical-Tag characterization.
- accepted SG5 staged comparable-lower-traffic evidence.
- accepted SG3 cap-sensitivity / positive-control evidence.

Do not modify, relabel, replace, or rerun these to create cleaner stage names.

## 3. Latest review anchors

Before execution, `git fetch origin` and verify actual remote heads. At this coordination point:

- SG1 whole-line/fairness: `e909f90a`
- SG3 downstream localization: `f1186336`
- SG5 lower-traffic observer: `f4077f46`
- SG4A has advanced beyond the older coordination anchor; treat its latest remote state as read-only and record the fetched HEAD.

If any remote branch advances again, use the newer state and record the delta. Never reset an advanced branch.

## 4. Completed scientific conclusions

### 4.1 Main performance

Primary FAST64 result remains frozen:

- IO / Base GM ≈ 1.326x
- OO / Base GM ≈ 1.592x

Negative/weak rows remain part of the evidence.

### 4.2 Capacity fairness

The accepted 80-KiB conventional-cache control shows that searchable locality capacity and DTC physical storage / miss concurrency are distinct resources.

A larger conventional cache wins some locality-sensitive workloads; DTC wins many others. Do not present TC80 as total-area matched.

### 4.3 Transaction granularity

The same-Core representative 32-B-sector vs 128-B-whole-line conventional controls are complete.

Paper-safe conclusion:

- transaction granularity materially affects some workloads;
- the direction is workload-dependent;
- it does not provide a uniform bias that explains DTC's overall performance result.

Do not start new granularity experiments.

### 4.4 Logical-Tag capacity

SG4A fixed G4 logical32/64 study is complete.

The logical80 point is a source-audited `LEGAL_WORKLOAD_DEPENDENT_DEADLOCK_BOUNDARY` for heavy workloads because equal logical/physical line counts provide no guaranteed free physical-line slack. It is not an indexing bug.

Do not rerun logical80 and do not expand SG4A to FAST12.

### 4.5 Comparable lower traffic

The staged paper-critical SG5 set is sufficient for the bounded claim that total lower-request count/payload alone does not explain DTC performance.

The GESUMMV/IO SG5 observer row has persistent non-scientific `exit -9` attempts. Do not retry it a third time.

### 4.6 Downstream cap sensitivity

SG3 bounded cap closure establishes:

- BICG and GESUMMV strongly benefit from reducing the GPU-wide DTC lower-outstanding cap from 8192 toward 2048/512.
- Btree and 2DConvolution are hurt by cap=512.
- therefore low cap is not universally beneficial.
- BICG receives partial benefit from larger L2 data capacity.
- BICG receives little/no meaningful benefit from 4x L2 MSHR entries.

Paper-safe current interpretation:

> DTC can create workload-specific downstream oversubscription / injection pressure after L1-side concurrency limits are removed.

Do not claim that a unique physical L2 bottleneck has already been isolated.

## 5. Phase-A telemetry and queue-headroom state

The accepted BICG telemetry gate showed:

- `MISS_QUEUE_FULL` falls strongly from default -> cap2048 -> cap512;
- lower-request lifetime and cycles improve in the same direction;
- L2 data/fill-port utilization is low and did not satisfy the original port trigger.

This legitimately triggered the predeclared queue=128 intervention.

Latest accepted partial result:

### BICG / OO / queue=128 / cap=8192

Compared with its accepted default queue=32 row:

- `MISS_QUEUE_FULL`: 43,594,150 -> 0
- cycles: 47,231,655 -> 47,588,121 (**+0.75%**, slightly worse)
- average lower lifetime: 5,612.70 -> 5,692.26 cycles (slightly worse)

This is strong intervention evidence for one bounded statement:

> Eliminating L2 miss-queue-full events is **not sufficient** to recover BICG/OO performance.

It does **not** prove that queue pressure is irrelevant to the full system. A finite queue can be a backpressure symptom of a slower downstream service path. Increasing buffering alone may remove queue-full events without increasing sustained service rate.

Therefore the open question is now explicitly a **buffering × downstream memory-service interaction** question.

## 6. Default modeled downstream configuration

Authority: SG3 source/config audit and FAST64 resolved configuration.

- 64 SM total.
- 20 memory channels/modules.
- 2 L2 subpartitions per memory channel = 40 L2 banks/subpartitions.
- per L2 bank: 128 sets × 16 ways × 128 B = 256 KiB.
- aggregate modeled L2 data capacity ≈ 10 MiB.
- L2 sector atom = 32 B.
- L2 MSHR = 192 entries/bank.
- MSHR merge limit = 4.
- L2 miss queue = 32 entries/bank.
- L2 data/fill port = 32 B/cache-cycle/bank.
- ROP delay = 200 cycles.
- DTC GPU-wide lower outstanding cap = 8192.
- DRAM clock = 850 MHz in the inherited Volta-like memory model.
- DRAM partition queues = 64:64:64:64.
- FR-FCFS DRAM scheduler queue = 64.
- DRAM return queue = 192.
- DRAM bus width = 16 B; burst length = 2.
- fixed `dram_latency` field = 100 plus source-defined DRAM timing parameters.

The FAST64 platform is a fixed **64-SM Volta-like trace-driven configuration derived from the Accel-Sim Volta model**, not a literal NVIDIA V100 configuration. Do not describe it as an exact V100.

## 7. Current open scientific question

The current question is no longer:

> Is the L2 miss queue alone the bottleneck?

BICG/OO already says no.

The current question is:

> Does DTC's high injection rate require both enough transient buffering and enough deeper memory-service capability before the exposed MLP can translate into performance?

The next stage must therefore separate:

1. queue buffering headroom;
2. downstream memory-service headroom;
3. their interaction.

This must be done with a small predeclared 2×2 experiment, not a broad memory-system sweep.

## 8. Immediate execution order

1. Let the already-running queue=128 family terminate naturally:
   - BICG/IO
   - GESUMMV/IO
   - GESUMMV/OO
   The accepted BICG/OO row remains immutable evidence.
2. In parallel, perform a **zero-simulation source audit + existing-telemetry audit** of the memory side after L2.
3. Select at most one clean source-defined memory-service headroom knob under the rules in `CODEX_NEXT_STAGE.md`.
4. Pre-register a BICG IO/OO queue × memory-service 2×2 design.
5. Run only the missing BICG cells authorized by that design.
6. Expand to GESUMMV only if the predeclared BICG validation gate is met.
7. Produce the review pack and stop.

## 9. Resource / failure discipline

- User authorizes aggressive compute use and will manage disk capacity.
- Do not use old free-space threshold bands as automatic scientific stop criteria.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- Preserve all failures.
- Use fresh UUIDs for any new simulator attempt.

## 10. Next project phase

After this bounded interaction study, the simulator mainline should freeze unless a result exposes a genuine scientific-contract issue.

Then priority moves to:

1. final paper-facing analysis/figure tables;
2. RTL/DC area/timing/SRAM evidence;
3. manuscript v0.3 and page-budget compression.
