# DTC-L1 / ISCAS 2027 Current State

Last coordination update: 2026-09-24

Status: **SIMULATOR MAINLINE NEAR-CLOSED; BOUNDED DOWNSTREAM-HEADROOM STUDY AUTHORIZED**

## 1. Current paper objective

The final objective is a high-quality ISCAS 2027 paper around Decoupled-Tag Cache (DTC), not an open-ended simulator campaign.

The paper should establish:

1. DTC decouples logical Tag visibility / miss state from physical data-line lifetime.
2. IO uses ordered completion/release; OO uses explicit dependency/reference-state tracking.
3. The main performance gain is real under a fixed 64-SM trace-driven platform.
4. The gain is not explained solely by extra physical storage, transaction granularity, or total lower traffic.
5. Higher L1-side concurrency can create workload-specific downstream oversubscription; the remaining question is whether one source-defined downstream resource can provide useful headroom while keeping the default DTC injection cap.

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
- SG3 downstream localization: `4f6e136e`
- SG4A logical-Tag: `42735258`
- SG5 lower-traffic observer: `f4077f46`

If a remote branch has advanced, use the newer state and record the delta. Never reset an advanced branch.

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

Examples already accepted:

- BICG comparable 128-B configurations have nearly equal lower work while cycles differ substantially.
- Btree / 2DConvolution can run much faster under DTC without having the minimum lower traffic.

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

Do **not** claim that a unique physical L2 bottleneck has already been isolated.

## 5. Default modeled downstream configuration

Authority: SG3 source/config audit.

- 64 SM total.
- 40 L2 banks/subpartitions.
- per bank: 128 sets × 16 ways × 128 B = 256 KiB.
- aggregate modeled L2 data capacity ≈ 10 MiB.
- L2 sector atom = 32 B.
- L2 MSHR = 192 entries/bank.
- MSHR merge limit = 4.
- miss queue = 32 entries/bank.
- data/fill port = 32 B/cache-cycle/bank.
- ROP delay = 200 cycles.
- DTC GPU-wide lower outstanding cap = 8192.

The DTC cap is GPU-wide, not per SM. Conventional variants do not consume this cap.

## 6. Current open scientific question

Before fully freezing simulator work, answer one final bounded question:

> Can a source-supported downstream resource enlargement recover DTC performance while preserving the original high DTC injection cap (8192)?

This is a **headroom** question, not a new broad sensitivity campaign.

The only candidate first-line resources are:

- L2 miss queue, if accepted telemetry shows coherent queue pressure.
- L2 data/fill port width, if accepted telemetry shows coherent port saturation.

No simulator run is authorized before the telemetry gate in `CODEX_NEXT_STAGE.md`.

## 7. Immediate execution order

1. Build the accepted BICG telemetry comparison table for:
   - default
   - L2 capacity 2x
   - L2 MSHR 4x
   - cap=2048
   - cap=512
   across IO/OO.
2. Interpret queue/port pressure using source-defined metrics only.
3. Apply the predeclared decision tree in `CODEX_NEXT_STAGE.md`.
4. Run at most the bounded queue/port headroom rows that the telemetry actually triggers.
5. Produce one review pack and stop at its decision boundary.

## 8. Resource / failure discipline

- User authorizes aggressive compute use and will manage disk capacity.
- Do not use old free-space threshold bands as automatic scientific stop criteria.
- Stop only for actual filesystem exhaustion / I/O risk.
- Never delete accepted/frozen evidence.
- Keep at most two heavy GESUMMV simulator processes concurrently.
- Preserve all failures.
- Use fresh UUIDs for any new simulator attempt.

## 9. Next project phase

After this bounded downstream-headroom decision, the simulator mainline should freeze unless a new result exposes a genuine scientific-contract issue.

Then priority moves to:

1. final paper-facing analysis/figure tables;
2. RTL/DC area/timing/SRAM evidence;
3. manuscript v0.3 and page-budget compression.
