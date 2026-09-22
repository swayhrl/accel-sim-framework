# REVIEW — 109 Native Translation Calibration Exact Pair V1R2

Date: 2026-09-22
Owner: ChatGPT
Status: ACCEPTED_WITH_SCOPE

## 1. Remote authority and integrity

Execution branch:

`hrl/awma-native-calibration-exact-pair-v1r2`

Remote HEAD:

`1d56c7ff12bd273f0f27c0de24d308a255b50b56`

The remote branch HEAD exactly matches the reported SHA.

The review pack contains five files listed by `SHA256SUMS`.
ChatGPT independently reconstructed and SHA256-hashed the exact remote file contents for all five entries:

`5 / 5 EXACT SHA256 MATCH`

The durable raw index reports:

- node164 bundle members: 10
- durable manifest SHA256:
  `f8f384e92da6a60e08f16f24cbbdcba75cbab339edb0a7ae57107c8cbf022f51`
- status:
  `DURABLE_SHA256_VERIFY_PASS_10_MEMBERS`

GitHub cannot independently re-read node164 filesystem bytes; that 10-member durable verification remains executor-side publication evidence.

## 2. Exact M1/M2 matched result

Frozen exact configuration:

```text
stride       = 4096 bytes
locations    = 4096
steps        = 512
samples      = 50 per warp
policy       = default
warmup       = 2
seed         = 102
M1 warps     = 1
M2 warps     = 16
```

Three independent process repetitions:

### M1

```text
rep1 median = 294.0 cycles/load
rep2 median = 294.5
rep3 median = 295.0
median-of-medians = 294.5
population CV of process medians = 0.139%
```

### M2

```text
rep1 pooled median = 279.0 cycles/load
rep2 pooled median = 282.0
rep3 pooled median = 281.0
median-of-medians = 281.0
population CV of process medians = 0.444%
```

Independent relative-change recomputation:

`(281.0 - 294.5) / 294.5 = -4.5840%`

The reported `-4.584%` is correct.

M2's 800 samples per process are 16 warps × 50 samples; the reported median is a pooled multi-warp sample median, not an aggregate throughput metric and not a direct per-warp-throughput measurement.

## 3. Updated Native concurrency interpretation

The previous V1R1 behavioral matrix showed strong one-warp -> sixteen-warp latency reduction at 1024 locations:

- 4 KiB stride: -33.73%
- 64 KiB stride: -38.64%
- 256 KiB stride: -28.39%
- 2 MiB stride: -35.95%

The exact representative 4096-location pair now shows only:

`-4.584%`

Therefore Native concurrency hiding is real but not uniform across working-set regimes.

The project-level Native interpretation should be narrowed from an unqualified:

`NATIVE_CONCURRENCY_HIDING_SUPPORTED`

to:

`NATIVE_CONCURRENCY_HIDING_PARTIAL / WORKING_SET_DEPENDENT`

This does not invalidate V1R1. It refines it:

- at the 1024-location regime, independent warp concurrency materially reduces observed dependent-chain cycles/load;
- at the 4096-location regime selected for the exact M1/M2 simulator-native pair, the same concurrency increase yields only a modest reduction.

No hidden TLB capacity, lookup latency, or throughput value is inferred.

## 4. Calibration consequence

The exact M1/M2 pair is now scientifically useful because Native and simulator input configurations match.

However, later Legacy/V1/V2 simulator comparison must align the observable.

Native V1R2 measures:

`clock64()-based cycles/load for each dependent chain sample`

The M2 result pools 16 warp-local chains.

Therefore do NOT compare Native 294.5/281.0 directly to total simulated kernel cycles.

The simulator cross-calibration should expose a semantically aligned quantity, for example:

- target warp / chain issue-to-completion cycles per dependent step;
- or another per-chain latency observable proven equivalent to the Native clock64 interval.

Overall simulated kernel cycles may be reported separately as throughput/context information, but not treated as the Native clock64 observable.

## 5. Readiness

Native calibration remains:

`READY_WITH_SCOPE`

Now with a fully matched M1/M2 exact configuration.

Admitted constraints for future simulator calibration:

1. strong working-set-dependent latency exposure exists;
2. concurrency hiding is substantial around the 1024-location regime;
3. concurrency hiding is weak/modest for the exact 4096-location M1/M2 pair;
4. cache policy materially changes the observed memory-hierarchy regime;
5. no direct Native TLB metric is available;
6. the four simulator-native microtraces are durable and qualified.

## 6. Next action

109 may remain idle.

Do not collect additional Native evidence before the current 174 V2 result returns.

After 174 V2 review, design one cross-calibration stage that consumes:

- Native V1R1 + V1R2;
- M0/M1/M2/M3 simulator-native traces;
- Legacy simulator semantics;
- V1 launch-overlap semantics;
- V2 READY-application semantics, if scientifically admitted.

No architecture mechanism is authorized yet.
