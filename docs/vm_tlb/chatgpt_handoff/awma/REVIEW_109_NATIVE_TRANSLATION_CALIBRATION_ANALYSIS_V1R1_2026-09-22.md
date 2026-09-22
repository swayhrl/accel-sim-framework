# REVIEW — 109 Native Translation Calibration Analysis V1R1

Date: 2026-09-22
Owner: ChatGPT
Status: ACCEPTED_WITH_SCOPE

## 1. Remote authority

Execution branch:

`hrl/awma-native-calibration-analysis-109-v1r1`

Remote HEAD:

`589d0d579e8e9d30922d3842084c3c50f09833d7`

Remote branch HEAD independently matches the reported SHA.

The review pack contains 11 files listed by `SHA256SUMS` plus the checksum file itself.
ChatGPT independently re-hashed all 11 listed remote file contents:

`11 / 11 EXACT SHA256 MATCH`

The CPU-only execution claim is consistent with the published `RUN_RECEIPTS.json`.

## 2. Native behavioral result

Accepted behavioral classification:

`NATIVE_CONCURRENCY_HIDING_SUPPORTED`

This is a behavioral memory-hierarchy result, not a direct TLB-latency/capacity measurement.

The 4 KiB-spacing dependent one-warp curve exposes a strong working-set effect:

```text
locations     median cycles/load
16                 52.0
512                52.0
1024              155.5
2048              245.5
4096              282.5
8192              302.0
16384             427.5
32768             644.5
```

Therefore a clear behavioral knee appears between 512 and 1024 locations in this exact benchmark realization.

Do not label that knee as a hardware TLB capacity; data-cache/memory and translation effects are not directly separated.

At 1024 locations, increasing from one warp to sixteen warps reduces median cycles/load consistently across four address spacings:

| stride | 1 warp | 16 warps | reduction |
|---|---:|---:|---:|
| 4 KiB | 166.0 | 110.0 | 33.73% |
| 64 KiB | 169.5 | 104.0 | 38.64% |
| 256 KiB | 155.0 | 111.0 | 28.39% |
| 2 MiB | 165.5 | 106.0 | 35.95% |

This supports Native latency hiding under independent warp-level concurrency.

Because the benchmark uses one dependent lane-0 chain per warp, this result should be interpreted as warp-level memory/translation latency exposure versus concurrency, not aggregate bandwidth and not a direct TLB throughput number.

## 3. Cache-policy / resource-control caveat

The default-vs-CG control materially changes realized latency:

`4 KiB / 1024 locations: 155.5 -> 293.0 cycles/load median`

Therefore cache/data-path policy is a substantial confounder and unlike policies must not be merged.

The V1R1 review correctly refuses to admit synthetic NCU numbers:

`NATIVE_MICROBENCH_RESOURCE_SUMMARY.tsv`

reports no selector-qualified durable numeric NCU resource rows.

Thus Native concurrency hiding is admitted as behavioral evidence only; it is not yet decomposed into translation versus data-cache/DRAM components.

## 4. Exact-target Native anchors

Accepted exact Native footprint for T0:

```text
raw dynamic records       13,490,624
memory instruction records 1,100,848
effective lane addresses  33,693,184
unique 4 KiB regions           3,625
unique 64 KiB regions            228
```

This now aligns the Native footprint evidence class across T0/T1/T2.

Exact timing anchors:

- T0 Q05: 152,717.0 ns mean, CV 4.567% — `MEASURED_WITH_VARIABILITY`
- T1 GEMM: 203,591.2 ns mean, CV 0.286% — `STABLE_NATIVE_TIMING_ANCHOR`
- T2 GEMV: 4,422.4 ns mean, CV 1.073% — `STABLE_NATIVE_TIMING_ANCHOR`

No Native-ns to simulator-cycle conversion is authorized.

## 5. Representative simulator-native traces

The following four traces are accepted as durable simulator-input candidates:

- M0_COMPACT
- M1_DEPENDENT_LARGE
- M2_MULTIWARP_HIGH
- M3_STRIDE64K

Each has:

- exact configuration label;
- source authority;
- selector identity;
- run ID;
- durable node164 path;
- common 76-member manifest verification authority;
- payload SHA256;
- record count;
- zero drop;
- zero overflow;
- xz integrity PASS;
- postprocess trace-format PASS;
- final durable admission.

These may be consumed by 174 after scientific-stage admission.

## 6. Important cross-calibration scope gap

The Native concurrency matrix used to establish the 1-warp -> 16-warp reduction is:

`4 KiB stride × 1024 locations`

However the selected representative trace pair is:

```text
M1_DEPENDENT_LARGE = 4 KiB stride × 4096 locations × 1 warp
M2_MULTIWARP_HIGH  = 4 KiB stride × 4096 locations × 16 warps
```

The current Native summary contains the exact M1 4096-location one-warp measurement:

`median = 282.5 cycles/load`

but no exact 4096-location sixteen-warp Native timing row.

Therefore the four traces are qualified simulator inputs, but M1/M2 do not yet form a fully exact Native-timing-matched pair.

This does not invalidate:

`NATIVE_CONCURRENCY_HIDING_SUPPORTED`

because the concurrency trend is independently supported across four spacings at 1024 locations.

It limits exact trace-to-Native calibration.

## 7. Readiness decision

Accepted:

`READY_WITH_SCOPE`

The evidence is ready for:

- workload/native footprint calibration;
- exact target Native timing anchoring;
- behavioral concurrency-hiding constraints;
- simulator execution of the four representative microtraces.

Before claiming an exact Native-vs-simulator M1/M2 matched comparison, close the single missing exact Native point:

`4 KiB stride × 4096 locations × 16 warps`

Prefer a contemporaneous M1 one-warp control in the same small run.

No new NVBit/trace capture is required.

## 8. 174 boundary

Do not start simulator cross-calibration while 174 V2 is still active.

When V2 returns, combine:

- Legacy;
- V1;
- V2;
- Native behavior;
- M0/M1/M2/M3 simulator-native traces.

No architecture mechanism is authorized before that review.
