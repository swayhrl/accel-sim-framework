# Agent A current uniform L2-factor cycle analysis

Snapshot: **2026-10-27 19:32:14 CST**. Read-only analysis; zero model launches or registrations.

Accepted source receipts: **117/350** ({'PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE': 111, 'REFERENCE_ACCEPTED_NO_NEW_START': 6}). Running snapshot: 58. Sources read over 2026-10-27T11:32:14.535551+00:00–2026-10-27T11:32:14.595666+00:00; atomic per-file reads, not a global filesystem transaction. AUTO_SUMMARY is an independently timestamped cross-check, not the source of raw cycles.

## Uniform-profile DH speedups

Speedup=DH_P0/DH_variant, >1 faster. Each row has its own explicit population; unequal row populations are not a ranking.

|Profile|Pairs/35|GM|Median|+/equal/−|Min–max|
|---|---:|---:|---:|---:|---:|
|E384|10/35|1.000000000|1.000000000|0/10/0|1.000000000–1.000000000|
|E768|10/35|1.000000000|1.000000000|0/10/0|1.000000000–1.000000000|
|M8|9/35|0.999533309|1.000000000|0/8/1|0.995807616–1.000000000|
|M16|9/35|1.000000000|1.000000000|0/9/0|1.000000000–1.000000000|
|Q64|9/35|1.000000000|1.000000000|0/9/0|1.000000000–1.000000000|
|Q128|10/35|1.000000000|1.000000000|0/10/0|1.000000000–1.000000000|
|F128|8/35|1.000000000|1.000000000|0/8/0|1.000000000–1.000000000|
|F256|8/35|1.000000000|1.000000000|0/8/0|1.000000000–1.000000000|

Common population across **all8** profiles: **5/35**. gaussian, histogram, heartwall, BlackScholes, lud.
Same-common-population GM: E384=1.0, E768=1.0, M8=0.9991601135988899, M16=1.0, Q64=1.0, Q128=1.0, F128=1.0, F256=1.0.

Non-P0 matched CH/DH quads: **0**. Missing CH variants remain null; neither CH system gains nor relative DTC improvements can yet be claimed.

## P0 CH/DH absolute-performance paired subset

This is a partially completed same-build P0 input subset, not the full suite. CH/DH>1 means DTC is faster. It is distinct from DH_P0/DH_variant above.

|Suite|Pairs/expected|GM CH/DH|Median|DTC faster/equal/slower|
|---|---:|---:|---:|---:|
|ALL|13/35|0.9871136327689253|1.0084848982496477|8/0/5|
|CUDA Samples|3/9|1.0201129231532318|1.0252419203516892|3/0/0|
|Parboil|1/7|0.9951249238269348|0.9951249238269348|0/0/1|
|PolyBench/GPU|3/9|0.8556612759024973|0.891739203807251|0/0/3|
|Rodinia|6/10|1.041535699863104|1.0210408176828931|5/0/1|

|Program|CH P0 cycles|DH P0 cycles|CH/DH|
|---|---:|---:|---:|
|ATAX|28428842|31880220|0.891739204|
|BICG|26298698|28685812|0.916784158|
|BlackScholes|8993|8971|1.002452346|
|dwt2d|73691|73071|1.008484898|
|gaussian|763932|740717|1.031341254|
|heartwall|8782|8551|1.027014384|
|histogram|101432|98202|1.032891387|
|lud|485866|478654|1.015067251|
|mergeSort|114742|111917|1.025241920|
|MVT|26581175|34687540|0.766303260|
|particlefilter_float|1861126|2100874|0.885881781|
|particlefilter_naive|511136|384601|1.329003305|
|sad|114310|114870|0.995124924|

Exact input identities for this subset: ATAX `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950`, BICG `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`, BlackScholes `b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0`, dwt2d `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008`, gaussian `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3`, heartwall `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980`, histogram `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58`, lud `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8`, mergeSort `dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48`, MVT `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`, particlefilter_float `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4`, particlefilter_naive `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e`, sad `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9`.

## Program results and what remains unknown

- BlackScholes (CUDA Samples, `b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0`): all 8 available paired factor results are **exactly equal integer cycles** to P0; missing: none. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- dwt2d (Rodinia, `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008`): all 7 available paired factor results are **exactly equal integer cycles** to P0; missing: Q64. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- gaussian (Rodinia, `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3`): all 8 available paired factor results are **exactly equal integer cycles** to P0; missing: none. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- histogram (CUDA Samples, `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58`): all 8 available paired factor results are **exactly equal integer cycles** to P0; missing: none. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- lud (Rodinia, `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8`): all 8 available paired factor results are **exactly equal integer cycles** to P0; missing: none. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- mergeSort (CUDA Samples, `dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48`): all 6 available paired factor results are **exactly equal integer cycles** to P0; missing: M8, F256. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- particlefilter_float (Rodinia, `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4`): all 7 available paired factor results are **exactly equal integer cycles** to P0; missing: F128. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- particlefilter_naive (Rodinia, `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e`): all 7 available paired factor results are **exactly equal integer cycles** to P0; missing: F128. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- sad (Parboil, `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9`): all 6 available paired factor results are **exactly equal integer cycles** to P0; missing: M16, F256. This is observed cycle insensitivity, not statistical insignificance or proof of an unconstrained resource.
- Sensitive observed: heartwall `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980`: {'E384': 1.0, 'E768': 1.0, 'M8': 0.9958076161639688, 'M16': 1.0, 'Q64': 1.0, 'Q128': 1.0, 'F128': 1.0, 'F256': 1.0}.

No paired data yet for: 2DCONV, 3DCONV, 3MM, ATAX, BICG, GEMM, GESUMMV, MVT, SYRK, bfs, convolutionSeparable, cutcp, fastWalshTransform, histo, hybridsort, lavamd, mri-q, myocyte, scalarProd, scan, sgemm, srad_v1, stencil, transpose, vectorAdd.

The outstanding PolyBench matrix/strided kernels, larger Rodinia and other pending programs may change both GM and which uniform factor is promising. ATAX/MVT/BICG entries are not inferred from old PQ or PS; those are different factors. In particular, 3MM/GEMM and 2DCONV/3DCONV must finish before judging preserved Hash gains or new concurrency benefits. None are skipped because current short/fast inputs appear neutral.

## Structural overhead and selection boundaries

Fixed data capacity10MiB, 40 L2 subpartitions, 20 DRAM/controller objects. Logical formulas: MSHR atom-key entries40E; request-reference upper bound40EM (merge includes first request); configured miss slots40Q; FRFCFS request slots20F. Physical area and actual queue occupancy are unknown.
E384/E768 double/quadruple baseline MSHR keys (15360/30720 versus7680). M8/M16 double/quadruple the per-key request list bound. Q64/Q128 double/quadruple configured miss slots (2560/5120 versus1280). F128/F256 double/quadruple FRFCFS slots (2560/5120 versus1280) AND increase shared credits/controller from255 to319/447. Partition FIFOs and DRAM850MHz stay fixed.
No final uniform candidate, plateau, physical upper bound or boundary-extension decision is justified by an incomplete subset with unchanged cycles. Continue the already registered matrix; use all applicable frozen inputs and matched CH verification before promotion.

## Evidence

- Matrix `/root/data/dtc_l2_mlp_exploration_20261027_v1/control/MATRIX_CURRENT.json` SHA256 `0ca2df7320392eb55eae1eecd23d2f5df0316df1cfc6e757d8dee9e27f0dcdf8`.
- Summary `/root/data/dtc_l2_mlp_exploration_20261027_v1/analysis/AUTO_SUMMARY.json` SHA256 `9d7cd1bb8acdaf168d93f762a28f7baea26e7ca9f080236eb12cfb19d7775526` (timestamp 2026-10-27T11:32:04.696622+00:00).
- Full captured receipt metadata and per-result path/SHA/raw gzip SHA: `SOURCE_SNAPSHOT.json`, SHA256 `1372a18ab807fd93ccfad4b127ebfe7212ec54fa6c0bc0fb1fc337b3114015b6`.
- Every per-program raw-cycle pair and exact input SHA is in `ANALYSIS.json/full_table`; the source receipt path/SHA accompanies each accepted cycle. Missing/unfinished values are null.
- Accepted identity: Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`.
- `../PARAMETER_CONTRACT.json` supplies exact source-file SHA and line ranges for parser, MSHR key/merge, miss admission, and credits coupling.
- Source validation errors: **0**. Historical results, repairs, original ledgers, controllers and budgets unchanged.

## Suite factor coverage

|Profile|Suite|Paired/expected|GM|+/equal/?|
|---|---|---:|---:|---:|
|E384|CUDA Samples|3/9|1.0|0/3/0|
|E384|Parboil|1/7|1.0|0/1/0|
|E384|PolyBench/GPU|0/9|None|0/0/0|
|E384|Rodinia|6/10|1.0|0/6/0|
|E768|CUDA Samples|3/9|1.0|0/3/0|
|E768|Parboil|1/7|1.0|0/1/0|
|E768|PolyBench/GPU|0/9|None|0/0/0|
|E768|Rodinia|6/10|1.0|0/6/0|
|M8|CUDA Samples|2/9|1.0|0/2/0|
|M8|Parboil|1/7|1.0|0/1/0|
|M8|PolyBench/GPU|0/9|None|0/0/0|
|M8|Rodinia|6/10|0.9993000456629864|0/5/1|
|M16|CUDA Samples|3/9|1.0|0/3/0|
|M16|Parboil|0/7|None|0/0/0|
|M16|PolyBench/GPU|0/9|None|0/0/0|
|M16|Rodinia|6/10|1.0|0/6/0|
|Q64|CUDA Samples|3/9|1.0|0/3/0|
|Q64|Parboil|1/7|1.0|0/1/0|
|Q64|PolyBench/GPU|0/9|None|0/0/0|
|Q64|Rodinia|5/10|1.0|0/5/0|
|Q128|CUDA Samples|3/9|1.0|0/3/0|
|Q128|Parboil|1/7|1.0|0/1/0|
|Q128|PolyBench/GPU|0/9|None|0/0/0|
|Q128|Rodinia|6/10|1.0|0/6/0|
|F128|CUDA Samples|3/9|1.0|0/3/0|
|F128|Parboil|1/7|1.0|0/1/0|
|F128|PolyBench/GPU|0/9|None|0/0/0|
|F128|Rodinia|4/10|1.0|0/4/0|
|F256|CUDA Samples|2/9|1.0|0/2/0|
|F256|Parboil|0/7|None|0/0/0|
|F256|PolyBench/GPU|0/9|None|0/0/0|
|F256|Rodinia|6/10|1.0|0/6/0|
