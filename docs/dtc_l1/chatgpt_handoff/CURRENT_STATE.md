# DTC-L1 / ISCAS 2027 Current State

Last coordination update: 2026-09-24

Status: **SIMULATOR MAINLINE NEAR-CLOSED; MEMORY-SIDE QUEUE-CHAIN + DRAM-SERVICE HEADROOM STUDY AUTHORIZED**

## 1. Current paper objective

The final objective is a high-quality ISCAS 2027 paper around Decoupled-Tag Cache (DTC), not an open-ended simulator campaign.

The paper should establish:

1. DTC decouples logical Tag visibility / miss state from physical data-line lifetime.
2. IO uses ordered completion/release; OO uses explicit dependency/reference-state tracking.
3. The main performance gain is real under a fixed 64-SM trace-driven platform.
4. The gain is not explained solely by extra physical storage, transaction granularity, or total lower traffic.
5. Higher L1-side concurrency can create workload-specific downstream oversubscription.
6. The final simulator question is whether finite buffering along the L2->memory path and detailed-DRAM service rate jointly limit how much DTC-exposed MLP becomes useful.

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
- accepted SG3 L2-miss-queue=128 four-row intervention.
- accepted SG3 detailed-DRAM busW diagnostic probe.

Do not modify, relabel, replace, or rerun these to create cleaner stage names.

## 3. Latest review anchors

Before execution, `git fetch origin` and verify actual remote heads. At this coordination point:

- SG1 whole-line/fairness: `e909f90a`
- SG3 downstream localization: `2c5802153b30f73ebabb5ad69dc44de055cd0497`
- SG4A: `7c0a90e`
- SG5 lower-traffic observer: `f4077f46`

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
- low cap is therefore not a universal optimum.
- BICG receives partial benefit from larger L2 data capacity.
- BICG receives little/no meaningful benefit from 4x L2 MSHR entries.

Paper-safe current interpretation:

> DTC can create workload-specific downstream oversubscription / injection pressure after L1-side concurrency limits are removed.

Do not claim that a unique physical L2 or DRAM bottleneck has already been isolated.

## 5. Accepted L2 miss-queue intervention

The L2-internal miss queue was enlarged from 32 to 128 entries/bank at default DTC cap=8192.

All four accepted rows show the same result:

- BICG IO: queue-full 145,882,748 -> 0; cycles +0.83%.
- BICG OO: queue-full 43,594,150 -> 0; cycles +0.75%.
- GESUMMV IO: queue-full 217,938,332 -> 0; cycles +0.04%.
- GESUMMV OO: queue-full 214,486,650 -> 0; cycles +0.69%.

Therefore:

> Eliminating L2-internal miss-queue-full events is not sufficient to recover end-to-end performance.

This does not prove that buffering is irrelevant. It can mean that backpressure simply moves to a later finite queue or service stage.

## 6. Reclassification of the accepted busW probe

The accepted `-gpgpu_dram_buswidth 16 -> 32 B` experiment is retained as diagnostic evidence but is **not** accepted as a discriminating 2x service-rate test for the dominant 32-B sector-read path.

Source reason:

- the L2 sector atom is 32 B;
- DRAM request size for the dominant sector-read path is 32 B;
- default `dram_atom_size = BL(2) * busW(16) * chips(1) = 32 B`;
- the detailed-DRAM data step already completes a 32-B request in one transfer;
- busW=32 makes the atom 64 B, but a 32-B request still completes in one step.

Therefore the null busW result must not be used to claim that doubling meaningful DRAM service capability has no effect.

## 7. Default downstream queue/service chain

Current FAST64 platform:

- 64 SM.
- 20 memory channels.
- 2 L2 subpartitions/channel = 40 L2 banks.
- aggregate L2 data capacity ≈ 10 MiB.
- L2-internal miss queue = 32 entries/bank.
- `gpgpu_dram_partition_queues = 64:64:64:64`, ordered as:
  - ICNT->L2 = 64
  - L2->DRAM = 64
  - DRAM->L2 = 64
  - L2->ICNT = 64
- FR-FCFS DRAM scheduler queue = 64/channel.
- DRAM return queue = 192/channel.
- memory-partition shared credit limit is source-coupled to scheduler-queue + return-queue capacity.
- DRAM clock = 850 MHz.
- core / ICNT / L2 clocks = 1410 / 1410 / 1410 MHz.
- detailed DRAM timing cycle counts remain the inherited Volta-like values.
- default DTC GPU-wide lower-outstanding cap = 8192.

The platform is a fixed **64-SM Volta-like trace-driven configuration derived from the Accel-Sim Volta model**, not a literal NVIDIA V100 configuration.

## 8. Current open scientific question

The next bounded question is:

> Are there finite queues later in the L2->memory path that merely move the backpressure downstream, and does removing those queue limits together with a genuine detailed-DRAM service-rate upper bound recover the DTC performance headroom?

This is now a **memory-side queue-chain + service-rate** experiment.

## 9. Immediate execution order

1. Perform a zero-simulation source/telemetry confirmation of the exact queue chain and existing BICG pressure counters.
2. Pre-register the six BICG interventions defined in `CODEX_NEXT_STAGE.md`.
3. Launch all authorized BICG IO/OO rows in rolling parallel execution; no result gate is needed between the six families.
4. Strict-validate each terminal row immediately.
5. Conditionally validate at most two informative configurations on GESUMMV using the predeclared gate/priority.
6. If the strongest all-queue + 2x-DRAM-service configuration is materially beneficial, optionally run the predeclared 20-MiB-L2 all-headroom ceiling point for BICG IO/OO.
7. Produce the review pack and STOP.

## 10. Resource / failure discipline

- User authorizes aggressive compute use and will manage disk capacity.
- Do not use old free-space threshold bands as automatic scientific stop criteria.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- Preserve all failures.
- Use fresh UUIDs for every new attempt.

## 11. Next project phase

After this bounded queue-chain/service experiment, freeze simulator exploration unless a result exposes a genuine scientific-contract issue.

Then priority moves to:

1. final paper-facing analysis/figure tables;
2. RTL/DC area/timing/SRAM evidence;
3. manuscript v0.3 and page-budget compression.
