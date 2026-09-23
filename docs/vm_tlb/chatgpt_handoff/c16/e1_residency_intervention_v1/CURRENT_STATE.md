# C16 E1 Residency-Intervention Stage — Current State V1

## Accepted evidence

Clean E1 producer:
`hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1`

Independent clean consumer:
`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Semantic NCU V1:
`hrl/c16-e1-semantic-ncu-109-v1@9ad003fff0d42b544d3a703eca4846364c13ccb6`

Cache-state repair V2:
`hrl/c16-e1-semantic-ncu-cache-state-repair-109-v1@8d1f62229cae15199793ba5569327cf1e83596f3`

Independent V2 consumer:
`hrl/c16-e1-semantic-ncu-v2-consumer-174new-v1@cdd3ec7afbb1611cc52a4b74d32b38a3edabd131`

## Closed findings

Under byte-identical FP16 activation inputs, Qwen2.5-7B shows a strong operator × M-shape × deployed-implementation interaction.

Independent timing ratios:

- q_proj:
  - M1 AWQ/RAW_FP16 = 0.9801257351
  - M256 = 1.3044559790
- down_proj:
  - M1 = 0.5010500375
  - M256 = 1.2758391297
- up_proj:
  - M1 = 0.4002389919
  - M256 = 1.8687647899

Application-replay/cache-control-none semantic NCU for up_proj independently closed:

| Metric | M1 AWQ/RAW | M256 AWQ/RAW |
|---|---:|---:|
| L1/TEX | 0.1737193764 | 3.3837209302 |
| L2 | 0.3054590374 | 3.0311223007 |
| DRAM | 4.6324305e-06 | 1.1395041417 |

Capacity consistency:

- AWQ up_proj packed state = 35,273,728 B
- device L2 = 67,108,864 B
- RAW FP16 up_proj dense weight = 135,790,592 B
- M1 AWQ DRAM = 640 B
- M1 RAW DRAM = 138,156,416 B

Accepted interpretation:

`CONSISTENT_WITH_WARM_CACHE_CAPACITY_RESIDENCY_HYPOTHESIS_NOT_CAUSAL_PROOF`

## Next scientific question

The next stage does not add a mechanism and does not start full tracing.

It asks:

> If the target semantic input/backend is held fixed, does deliberately perturbing pre-target memory/cache state reversibly change timing and traffic in the pattern predicted by the warm-residency hypothesis?

A secondary control asks whether a large-cache-line-footprint perturbation differs from a sparse page-footprint perturbation over the same allocated address range.

This stage is one combined node109 Goal plus one parallel node174 consumer/prep Goal.

No NVBit/full address trace/cache-TLB mechanism is authorized.


---

## Producer residency-intervention completed

node109 producer:

`hrl/c16-e1-residency-intervention-109-v1@22d1b98d7f0c213950654fc754be4e7388836de3`

Producer closed:

- exact q/down/up capacity census;
- WARM/SPARSE/DENSE/WARM_B native intervention timing;
- semantic NCU under application replay/cache-control none;
- up_proj M1 pressure-dose timing and bounded 64 MiB NCU;
- accepted CODE down_proj M1 holdout;
- no NVBit/full trace/mechanism work.

Producer scoped label:

`RESIDENCY_INTERVENTION_PARTIALLY_SUPPORTED`

Primary TEXT up_proj M1 AWQ producer gates:

- MATERIAL_TIMING_PERTURBATION = true
- MATERIAL_DRAM_PERTURBATION = true
- DENSE_SPECIFIC = true
- REVERSIBLE = false

Important nuance:

`WARM_B/WARM_A = 0.937499981...`

The preregistered equality-style recovery gate therefore fails by the strict 5% rule, even though WARM_B is **faster**, not persistently dense-slow. Preserve the preregistered boolean/label exactly; discuss this only as interpretation nuance, not as a post-hoc relabel.

Producer key observations:

- up_proj M1 AWQ DENSE/WARM timing ≈ 1.53646
- SPARSE/WARM ≈ 0.97656
- DRAM WARM 80,000 B
- DRAM SPARSE 2,365,312 B
- DRAM DENSE 35,368,192 B
- up_proj M256 AWQ DENSE/WARM ≈ 0.99230
- up_proj M1 AWQ dose response rises to ≈1.64× by 64 MiB and then approximately plateaus
- RAW dose response remains below 0.8%
- CODE down_proj M1 AWQ reproduces dense timing/DRAM perturbation and passes the recovery gate

Capacity census:

- q_proj RAW_FP16 < L2 and AWQ < L2
- down_proj RAW_FP16 > L2 and AWQ < L2
- up_proj RAW_FP16 > L2 and AWQ < L2

The existing 174-new prep branch is:

`hrl/c16-e1-residency-intervention-consumer-174new-v1@1beae7f0ed9c1d3de3829a6ff75ff0317ac1f503`

It should now resume and consume producer raw evidence directly.
