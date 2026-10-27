# L2 MLP First Results — Independent Read-only Check

Snapshot: 2026-10-27 18:53:10 CST. This is an in-flight subset, not a final suite result.

- Initial matrix: 350 cells = 35 frozen representative inputs × (CH P0 + DH P0 + eight DH variants). Six proven matching P0 references require no new starts; fresh registered budget = 344.
- Observed accepted results: 29 fresh strict/archive/native-restore PASS + 6 proven references = 35/350 (10.0%) cells, across 12/35 inputs.
- 477 independent consistency checks passed, zero failed checks. Engineering files: 0; FAIL results: 0.
- Controller snapshot: 59 starts consumed, 285 initial starts unspent; 32 running, 2 postprocessing. Concurrent files are sampled at different instants; do not add these to older summary counts as a single atomic transaction.

## What can be said now

The accepted short jobs are not representative of all 35 inputs. At the recorded summary snapshot, every non-P0 DH speedup population is n=0 because matching DH-P0 results for those completed variants are not yet accepted. Their GM is correctly null. CH-P0 / DH-variant would mix a design change with the L2 parameter change and must not be labelled DH L2 speedup.

Only ATAX, MVT and BICG currently have complete P0 CH/DH pairs, all via legal references. Their P0 CH/DH GM of 0.855661 describes those three diagnostic inputs only. It is not the 35-input suite GM. Variant CH matched controls are intentionally not yet present.

Several short programs have exactly equal cycles across E384/E768 or F128/F256; this is an observed equality between those variants, not proof of zero gain versus missing DH-P0. heartwall DH M8 has 8,587 cycles versus 8,551 in E384/E768/M16/F128/F256; do not select a per-program winner to construct a unified suite GM.

## Strict and archive evidence

For each fresh PASS this independent check compared result proof with L2_STRICT.json, the qualification proof SHA, natural zero-exit DONE and NATIVE_EXIT, compressed raw SHA, exact frozen input/population/build/clocks, the canonical archive receipt, manifest entry count and native-restore existence. It did not run models, redo archive transfers, or rewrite receipts. Existing strict/archive/native-restore acceptance is retained; the check is an additional receipt consistency audit, not a newly invented acceptance rule.

All six P0 references have the six required proofs (strict, natural completion, archive/native restore, complete options, source/binary, input/scope). No old accepted result or repair identity was promoted into a fresh result.

## Missing or limited observations

- L2 read sectors, read miss sectors, DRAM read atoms/bytes, aggregate L2 reservation failures and gpu_stall_dramfull are present in all 35 accepted records.
- Distinct L2 MSHR entry-full versus merge-full reason counters: missing in all 35 records. Aggregate rejection counts cannot identify the precise MSHR reason.
- avg_mrq_latency: absent in 27/35 proof records. Targeted closed raw inspection confirms those printed fields are absent; missing is not zero. Stored latency values use the last printed occurrence and must not be described as a weighted whole-application average.
- DRAM_n_ref_event carries an UNAVAILABLE/uninitialized sentinel and is invalid for numerical analysis, even though the JSON field exists.

## Frozen prelaunch declaration versus actual evidence

BUILD_PROFILE.json SHA `43cad5f44fb7d3302d9b2f897bacd0129d4caf3c3b2b5ce56964a72c7299e3eb` retains `native_values="UNPROVEN"`. This is an immutable prelaunch declaration. Completed strict records independently validate the observed 270 effective options, actual sources/binary, natural completion and declared trace population. The stale declaration does not invalidate that actual configuration evidence, and this audit leaves it unchanged. Whole-application numerical correctness remains separately UNPROVEN.

## Accepted cells

| Program | Suite | Cell | Profile | Cycles | Identity |
|---|---|---|---|---:|---|
| ATAX | PolyBench/GPU | CH | P0 | 28428842 | `eededb785179fc04` |
| ATAX | PolyBench/GPU | DH | P0 | 31880220 | `eededb785179fc04` |
| BICG | PolyBench/GPU | CH | P0 | 26298698 | `ae34174fbbdf83b2` |
| BICG | PolyBench/GPU | DH | P0 | 28685812 | `ae34174fbbdf83b2` |
| BlackScholes | CUDA Samples | CH | P0 | 8993 | `b31a85e4eb8d32ef` |
| BlackScholes | CUDA Samples | DH | E384 | 8971 | `b31a85e4eb8d32ef` |
| BlackScholes | CUDA Samples | DH | E768 | 8971 | `b31a85e4eb8d32ef` |
| BlackScholes | CUDA Samples | DH | F128 | 8971 | `b31a85e4eb8d32ef` |
| BlackScholes | CUDA Samples | DH | F256 | 8971 | `b31a85e4eb8d32ef` |
| dwt2d | Rodinia | CH | P0 | 73691 | `e5638b94095098ac` |
| dwt2d | Rodinia | DH | E384 | 73071 | `e5638b94095098ac` |
| dwt2d | Rodinia | DH | E768 | 73071 | `e5638b94095098ac` |
| dwt2d | Rodinia | DH | M8 | 73071 | `e5638b94095098ac` |
| dwt2d | Rodinia | DH | F128 | 73071 | `e5638b94095098ac` |
| gaussian | Rodinia | CH | P0 | 763932 | `16f4c42373e4961e` |
| gaussian | Rodinia | DH | E384 | 740717 | `16f4c42373e4961e` |
| gaussian | Rodinia | DH | E768 | 740717 | `16f4c42373e4961e` |
| heartwall | Rodinia | CH | P0 | 8782 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | E384 | 8551 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | E768 | 8551 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | M8 | 8587 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | M16 | 8551 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | F128 | 8551 | `731af5428c4b8155` |
| heartwall | Rodinia | DH | F256 | 8551 | `731af5428c4b8155` |
| histogram | CUDA Samples | CH | P0 | 101432 | `3722a5c85d91a948` |
| histogram | CUDA Samples | DH | Q64 | 98202 | `3722a5c85d91a948` |
| lud | Rodinia | CH | P0 | 485866 | `b33381cf25d44359` |
| lud | Rodinia | DH | F128 | 478654 | `b33381cf25d44359` |
| mergeSort | CUDA Samples | CH | P0 | 114742 | `dd9f695c4f53b083` |
| mergeSort | CUDA Samples | DH | E384 | 111917 | `dd9f695c4f53b083` |
| mergeSort | CUDA Samples | DH | E768 | 111917 | `dd9f695c4f53b083` |
| MVT | PolyBench/GPU | CH | P0 | 26581175 | `f437190767aaed49` |
| MVT | PolyBench/GPU | DH | P0 | 34687540 | `f437190767aaed49` |
| particlefilter_float | Rodinia | CH | P0 | 1861126 | `b41cc74c66ca6ed4` |
| particlefilter_naive | Rodinia | CH | P0 | 511136 | `3f85d1878aba9f04` |

Machine-readable `first_results.json` includes full input SHA, cohort, UUID, result SHA/path, counters, coverage, check counts and snapshot hashes. Seven unresolved identities remain outside this fixed 35-input experiment; no resolution or promotion is implied.
