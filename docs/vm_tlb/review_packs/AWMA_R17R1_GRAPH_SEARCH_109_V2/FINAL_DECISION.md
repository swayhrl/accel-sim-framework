# R17R1 final scientific decision — node109

**`R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT`** for this fixed quality-qualified, resident single-GPU search question. The prior V1 recall stop remains a baseline-qualification stop, **not** a graph-search performance negative.

## Quality repair without changing the index

The accepted normalized GloVe-100-angular base/query/official GT, `cuvs-cu12==26.8.1`, exact stable source, IVF-PQ graph SHA256 `a68d4a2905fcab13a40872db73165fb4271a493f09b9fd61f5f1e9a401f073b8`, and serialized index SHA256 `6cddddb35f63d31b1308d1411d76aabcef910b11caea1778ca823f4fb63e7151` were reverified before GPU work. Discovery queries remained 0..255; holdout 256..511 remained sealed. The stable benchmark-base YAML does use NN_DESCENT, but the bounded Stage-A completion on the **existing** index already crossed the unchanged recall@10≥0.95 gate:

| IVF-PQ extension, Q1 | Discovery recall@10 |
|---|---:|
| SINGLE_CTA 128/1 | 0.880859 |
| SINGLE_CTA 256/1 | 0.928906 |
| SINGLE_CTA 512/1 | **0.959766** |
| MULTI_CTA 512/1 | **0.961328** |

Thus A2 widths and the conditional NN_DESCENT second index were **not** run. No third index or build tuning exists. Candidate freeze used the lowest-search-effort qualified point of each mode, both 512/1; AUTO at this Q1 shape source-resolves to the same MULTI_CTA plan and was not a third arm.

## Formal Q1 and matched Q1/Q32 facts

The corrected formal paired protocol used three groups, two warmups then five formal repeats per arm/group, all 256 discovery queries as **individual** searches per repeat, and alternating arm order. Query/output arrays were device-resident/preallocated; a cuVS `Resources` handle was reused. Both arms reproduced recall≥0.95 in every formal repeat. Median complete host time per 256 Q1 searches was **56.110419 ms** (MAD 0.089072) for MULTI_CTA and **704.184787 ms** (MAD 0.078683) for SINGLE_CTA. `Q1_STRONG_V2` is explicit MULTI_CTA 512/1. These modes may perform different search work; this is mature software-mode selection, not a pure traversal-state intervention.

Under that **same explicit** strong mode/itopk/width, matched characterization found:

| Request | Complete host request/batch median | p95 | Recall range across formal repeats |
|---|---:|---:|---:|
| Q1, one query | **0.215450 ms** | 0.247351 ms | 0.959766–0.961328 |
| Q32, entire 32-query batch | **0.530881 ms** | 0.577366 ms | 0.965234–0.967578 |

The complete Q1 request is faster in absolute completion time than the complete Q32 batch. The much better Q32 amortized throughput is not divided by 32 to invent a single-query latency bound. After the strong mode and resource reuse, this screen found no material, unexplained **complete-request latency** loss that would justify GPU-local residual localization. It does not prove CAGRA universally optimal or rule out all traversal improvements.

Attempt0 formal timings with per-call Python `Resources` creation were retained only as an engineering control; source and corrected attempt1 explain why they are not the strongest baseline. The host submit interval in the corrected path may contain synchronized GPU work and cannot be called a wrapper-only percentage. A custom-stream GPU-event probe did not qualify, so pure GPU-active time is unavailable; no host/compute/memory bottleneck label is inferred. Stage D met the software-sufficient STOP before conditional C harness, persistent control, NSYS/NCU and holdout. No NVBit, second dataset, Jasper port, 174/Accel-Sim, or hardware mechanism was started.
