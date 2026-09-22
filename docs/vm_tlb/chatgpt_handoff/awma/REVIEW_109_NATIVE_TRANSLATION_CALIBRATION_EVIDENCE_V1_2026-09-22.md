# REVIEW — 109 Native Translation Calibration Evidence V1

Date: 2026-09-22
Owner: ChatGPT
Status: CAPTURE_ACCEPTED_WITH_SCOPE / SCIENTIFIC_ANALYSIS_PENDING

## 1. Remote publication independently verified

Execution branch:

`hrl/awma-native-calibration-evidence-v1`

Remote HEAD:

`724ca2b583495c87d9cfb59e277caf81fcecec1d`

The branch remote HEAD exactly matches the reported commit.

The published review pack contains 15 entries in `SHA256SUMS`. ChatGPT independently re-hashed all 15 remote file contents and obtained:

`15 / 15 EXACT SHA256 MATCH`

Therefore the Git review-pack publication is accepted.

The pack reports:

- T0 Route-B durable ACK PASS:
  - 21 files
  - 121,445,369 bytes
  - ACK SHA256 `75669dd620bf1f97dabc56e62afc1d44418a13055bfe40c2fdb0c949bdcdae9b`;
- NSYS timing + microbenchmark + four simulator-native microtrace durable bundle:
  - node164 `sha256sum -c SHA256SUMS`
  - 76 members OK.

GitHub does not directly expose node164 filesystem bytes, so the node164 raw-payload verification is accepted as executor-side durable-publication evidence rather than independently re-read by ChatGPT.

## 2. Exact-target Native timing

Fresh lightweight NSYS timing:

| Target | Run1 ns | Run2 ns | Run3 ns | Run4 ns | Run5 ns | Mean ns | CV |
|---|---:|---:|---:|---:|---:|---:|---:|
| T0 Q05 FlashAttention | 148512 | 164032 | 152769 | 152544 | 145728 | 152717.0 | 4.567% |
| T1 Prefill GEMM | 203009 | 203873 | 204256 | 203873 | 202945 | 203591.2 | 0.286% |
| T2 Decode GEMV | 4416 | 4480 | 4352 | 4416 | 4448 | 4422.4 | 1.073% |

Assessment:

- T1: stable Native timing anchor.
- T2: stable Native timing anchor.
- T0: measured and useful, but noticeably more variable. It should not be used for fine-grained cycle-to-time fitting or a precision baseline without additional stability evidence.

No simulator-cycle to nanosecond conversion is authorized.

## 3. Direct translation counter status

NCU 2025.1.1.0 on the RTX4080 exposed no admitted direct metric matching the intended TLB/MMU/GMMU/page-translation concept.

Accepted classification:

`DIRECT_TRANSLATION_COUNTER_UNAVAILABLE`

Therefore NCU may constrain data-cache/L2/DRAM/occupancy confounders but cannot directly provide a Native TLB hit rate or translation latency.

## 4. Exact-target NCU status

The pack reports:

- T1: `SELECTED_SINGLE_MATCH`
- T0: `NCU_TARGET_SELECTOR_UNRESOLVED`
- T2: `NCU_TARGET_SELECTOR_UNRESOLVED`

Therefore only T1 exact-target NCU evidence is currently scientifically admissible.

T0/T2 NCU files must not be interpreted as exact-target resource evidence.

No fresh NCU run is required merely for symmetry at this point.

## 5. T0 Native address evidence

A fresh exact T0 Route-B capture is accepted as a producer artifact:

- raw records = 13,490,624
- zero drop/overflow
- trace SHA256 = `48d2485ceddc44203c31b29ff365b400874c9e0fa754888aea14392f5d02cd904`

However the review pack explicitly states that exact T0 page aggregation remains pending accepted parser invocation.

Therefore:

`T0_NATIVE_CAPTURE_ACCEPTED_PAGE_FOOTPRINT_ANALYSIS_PENDING`

Do not import simulator-derived page counts into the Native evidence class.

## 6. Native microbenchmark capture

The committed source is suitable for the intended behavioral reconnaissance:

- dependent pointer/address chain;
- configurable stride and working-set size;
- multiple independent warp-local chains;
- per-load `clock64()` timing;
- optional cache-global load policy;
- deterministic permutation seed;
- compact / large / multi-warp / 64 KiB-spacing configurations.

Important semantic limitation:

The measured `cycles_per_load` includes the realized Native memory hierarchy behavior (translation + cache/memory + dependency effects). It is not a direct TLB latency measurement.

The current review pack does not contain the numeric Native microbenchmark result matrix. It only points to:

- `NATIVE_TLB_RECON_RAW_CORE.tsv`
- `NATIVE_TLB_RECON_FOLLOWUPS.tsv`

Likewise the NCU resource-control table only records that resource data were captured, not the actual values.

Therefore the key calibration question cannot yet be independently answered from the Git review pack:

> Does dependent single-chain behavior degrade with page working set while multi-warp independent chains hide a substantial fraction of that latency?

Accepted status:

`NATIVE_MICROBENCH_CAPTURE_COMPLETE_ANALYSIS_PENDING`

## 7. Representative simulator-native microtraces

Four representative traces are listed:

- M0_COMPACT — 4K stride, 16 locations, 1 warp
- M1_DEPENDENT_LARGE — 4K stride, 4096 locations, 1 warp
- M2_MULTIWARP_HIGH — 4K stride, 4096 locations, 16 warps
- M3_STRIDE64K — 64K stride, 1024 locations, 1 warp

The pack marks all four as:

`ACCEPTED_ZERO_DROP`

and the durable ACK says the four microtrace bundles are included in the 76-member verified publication.

However the compact Git pack does not provide, per trace:

- exact selector receipt;
- durable path/run ID;
- payload SHA;
- manifest SHA;
- grammar validation result;
- xz integrity result;
- drop/overflow counters;
- exact binary/source/config identity.

These should be exported before 174 consumes the traces as calibration inputs.

No recapture is authorized unless the existing durable artifacts fail deterministic verification.

## 8. Scientific stage classification

Operational capture/publication stage:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_EVIDENCE_109_V1_CAPTURE_ACCEPTED_WITH_SCOPE`

Scientific calibration interpretation:

`ANALYSIS_PENDING`

This is not a failure and does not require another GPU campaign.

The missing work is deterministic CPU-only analysis of already durable evidence.

## 9. Next action

Run one CPU-only closeout continuation on 109/node164:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_109_V1R1`

It must:

1. summarize the raw Native microbenchmark sweep numerically;
2. quantify dependent-vs-multiwarp scaling and working-set/stride knees;
3. join the representative NCU resource-control values where selectors/evidence allow;
4. invoke the accepted Route-B parser on exact T0 to close Native page footprint;
5. export per-microtrace selector/hash/xz/zero-drop receipts;
6. not rerun GPU timing, NCU, NVBit, or simulator-native capture unless deterministic verification proves an existing artifact invalid.

After this closeout, the Native evidence can be used directly as a formal external-calibration input for 174 Legacy/V1/V2 comparison.
