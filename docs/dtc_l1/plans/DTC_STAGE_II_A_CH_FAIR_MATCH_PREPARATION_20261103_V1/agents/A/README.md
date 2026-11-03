# CH-F128/F256 candidate design and qualification

This is a planning-only package. No scientific request, model grant, UUID, simulator launch or owner change was made. The existing 70 AD1 proposals are read-only references, not promoted or reused as new execution identities.

## Frozen identity and evidence

Original350 is 331 accepted = 325 fresh strict + 6 previously ratified identical P0 references, 18 archived negatives, and 1 typed scan M16 engineering negative. Native AUTO_SUMMARY still labels the typed engineering slot PENDING; its guard is preserved separately. The independent336 named view is not imported. Final closure authority is `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`; the earlier plan `5ba029e60c2e7523b193043b345990c7ae52531c` was a 330/335 timestamped snapshot and is not rewritten.

Core `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`, binary `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`; binary/library bytes were rehashed but never executed. DRAM850MHz; core/ICNT/L2 clocks1410MHz; L2 40×256KiB=10MiB.

## Exact factor and fairness

`-gpgpu_frfcfs_dram_sched_queue_size` is the only changed CH effective option:64→128 or256. MSHR192, merge4, missQ32; partition FIFOs64:64:64:64, returnQ192, all timing/mapping remain fixed. Fixed source l2cache.cc131–147 makes shared credits F+192−(2−1):255→319→447/controller. Private limit is1/subpartition (2 private slots/controller). It is a coupled scheduler-capacity/shared-credit probe.

CH and DH have seven deliberate L1 configuration differences, reproduced exactly in CONFIG_QUALIFICATION.json: conventional CH line geometry/policy, declared unified L1 size, mode, finite service, DTC MSHR, PIB, Tag hash. Inactive DTC options under CH are not claims of actual CH DTC structures. CH declared unified96KiB versus DH128KiB are configuration quantities, not proof of comparable area. DH physical pool640×128B=80KiB/SM is distinct from its512 logical Tag slots; no iso-area/timing/power claim. Hash families and all non-L1 downstream options are preserved.

## Partition and batching

64 core proposed CH cells = same32 inputs ×F128/F256, possessing original CH-P0,DH-P0,DH-F128,DH-F256. Two supplements: hybridsort F256 (F128 original negative), lavamd F128 (CH-P0 original negative, therefore no normalized CH/four-way benefit). Four deferred: hybridsortF128,lavamdF256,SYRKF128/F256. No original/IR/R2 substitution; no per-program best-configuration GM.

First batch proposal: convolutionSeparable, scan, 2DCONV, ATAX, MVT, BICG, vectorAdd, GEMM × bothF =16. Selection is explicit mechanism/control coverage and does not change the fixed final35 or core32 population. Remaining48 core execution batches may only be defined after separately authorized first16 and review. Supplements stay separate; lavamd requires independent high-memory approval.

## Input and CPU-only qualification

35 complete declared trace SHA contracts, input binding SHA, commandlist SHA, expected kernels/CTA/instructions, prior scope and captured-extent caveats are recorded. Current commandlists rehashed and member readability checked; large trace bodies were not redundantly reread. Existing complete-body SHA receipts do not certify numerical values, exact capture ELF, or full native end-to-end application.

777 successful loop assertions repeat nine invariant families over35inputs and70candidates: population cardinality, input binding SHA, commandlist SHA, trace member readability, parent config SHA, generated SHA, CH/DH L1 contract, exact downstream equality, and final partition/acceptance cardinality. They are not777 independent scientific observations. A separate CPU executable linked only pinned option_parser.cc:6 positive CH/DH×P0/F128/F256 and3 rejecting clock/capacity/unlimited fixtures. No simulator/cache engine instantiated.

## Resource and archive release gates

RESOURCE_AND_ARCHIVE_QUALIFICATION.json retains original DONE success/failure RSS and elapsed times; proposed reservation=max(4GiB,1.25×largest observed same-inputRSS+1GiB). It is a conservative planning estimate, not an admission cap or runtime guarantee; elapsed history includes contention and failed runs, so no definite new-run ETA is claimed. Archive/log paths remain native epoch2 plus true164; formal future acceptance requires strict natural-completion, exact configuration/input/build, archive SHA and native-restore receipts. New scientific identity, execution approval, live host/cgroup/NUMA admission and CH runtime liveness remain UNQUALIFIED.

| Program | Input prefix | CH-P0 | DH-P0 | DH-F128 | DH-F256 | F128 candidate | F256 candidate | Max observed RSS GiB |
|---|---|---:|---:|---:|---:|---|---|---:|
| 2DCONV | d984ea5475a581ad | 1548909 | 462740 | 437573 | 429253 | CORE | CORE | 0.570 |
| 3DCONV | 79f8ab6241faeed6 | 2958083 | 2200332 | 2205628 | 2211632 | CORE | CORE | 0.562 |
| 3MM | 977a2f7007cb1f96 | 4191465 | 2402871 | 2402871 | 2402871 | CORE | CORE | 4.332 |
| ATAX | eededb785179fc04 | 28428842 | 31880220 | 31894637 | 31321955 | CORE | CORE | 2.270 |
| BICG | ae34174fbbdf83b2 | 26298698 | 28685812 | 29210480 | 28883488 | CORE | CORE | 2.309 |
| BlackScholes | b31a85e4eb8d32ef | 8993 | 8971 | 8971 | 8971 | CORE | CORE | 0.590 |
| GEMM | fc0705ae3721e999 | 1395216 | 826089 | 826089 | 826089 | CORE | CORE | 4.781 |
| GESUMMV | 769e6d9fd5f9cd53 | 114860845 | 89502220 | 86464623 | 90151547 | CORE | CORE | 2.902 |
| MVT | f437190767aaed49 | 26581175 | 34687540 | 35332620 | 35093446 | CORE | CORE | 2.266 |
| SYRK | b51811aca9dc70cf | FAIL_L2MLP_ARCHIVED_NO_RETRY | FAIL_L2MLP_ARCHIVED_NO_RETRY | FAIL_L2MLP_ARCHIVED_NO_RETRY | FAIL_L2MLP_ARCHIVED_NO_RETRY | DEFERRED | DEFERRED | 9.146 |
| bfs | 1df9d5479504d9c7 | 4330430 | 4170294 | 4170294 | 4170294 | CORE | CORE | 2.500 |
| convolutionSeparable | 4114a3dc0d06b55b | 825151 | 800572 | 674364 | 562886 | CORE | CORE | 1.281 |
| cutcp | af7320f9d9dc6629 | 4502965 | 4490473 | 4490473 | 4490473 | CORE | CORE | 13.283 |
| dwt2d | e5638b94095098ac | 73691 | 73071 | 73071 | 73071 | CORE | CORE | 0.477 |
| fastWalshTransform | f7f22a2ccc836a8a | 191732 | 185317 | 185382 | 185740 | CORE | CORE | 0.992 |
| gaussian | 16f4c42373e4961e | 763932 | 740717 | 740717 | 740717 | CORE | CORE | 0.426 |
| heartwall | 731af5428c4b8155 | 8782 | 8551 | 8551 | 8551 | CORE | CORE | 0.492 |
| histo | 2c506bf13c81ff5d | 5636037 | 5865589 | 5789155 | 5731388 | CORE | CORE | 2.182 |
| histogram | 3722a5c85d91a948 | 101432 | 98202 | 98202 | 98202 | CORE | CORE | 0.926 |
| hybridsort | 09f94fcc7494a03b | 18575969 | 18563916 | FAIL_L2MLP_ARCHIVED_NO_RETRY | 16370955 | DEFERRED | SUPPLEMENT | 11.593 |
| lavamd | ddb6806316876a85 | FAIL_L2MLP_ARCHIVED_NO_RETRY | 5629432 | 5629432 | FAIL_L2MLP_ARCHIVED_NO_RETRY | SUPPLEMENT | DEFERRED | 67.336 |
| lud | b33381cf25d44359 | 485866 | 478654 | 478654 | 478654 | CORE | CORE | 0.539 |
| mergeSort | dd9f695c4f53b083 | 114742 | 111917 | 111917 | 111917 | CORE | CORE | 0.488 |
| mri-q | dc7a91531846c113 | 362244 | 360174 | 359855 | 359855 | CORE | CORE | 4.027 |
| myocyte | 977e34578994c3d2 | 145909578 | 145147976 | 145147976 | 145147976 | CORE | CORE | 0.469 |
| particlefilter_float | b41cc74c66ca6ed4 | 1861126 | 2100874 | 2100874 | 2100874 | CORE | CORE | 1.066 |
| particlefilter_naive | 3f85d1878aba9f04 | 511136 | 384601 | 384601 | 384601 | CORE | CORE | 0.770 |
| sad | db89be14146b9163 | 114310 | 114870 | 114870 | 114870 | CORE | CORE | 1.258 |
| scalarProd | 2b93f70cd0666c51 | 420477 | 411009 | 411440 | 409181 | CORE | CORE | 9.266 |
| scan | 6df3a84b612086e8 | 6710840 | 6648993 | 5748280 | 5179817 | CORE | CORE | 0.848 |
| sgemm | ffc8a89493c8a211 | 448633 | 409417 | 409417 | 409417 | CORE | CORE | 15.246 |
| srad_v1 | 0e62c67daa020853 | 8043823 | 7324411 | 7324411 | 7324411 | CORE | CORE | 0.913 |
| stencil | c885293ad99e21ee | 4965921 | 4662889 | 4662889 | 4662889 | CORE | CORE | 0.668 |
| transpose | 65151d2c661f88f3 | 241346 | 237820 | 237820 | 237820 | CORE | CORE | 0.699 |
| vectorAdd | e7bb67e63e3c3847 | 220803 | 217305 | 213053 | 236217 | CORE | CORE | 0.602 |

For every future metric publish exact input intersection and n/35, suite coverage, sign/ties/missing. DirectF128/F256 comparisons use their jointly accepted population. New CH cycles and gains remain UNKNOWN until separately approved simulations. No performance can be inferred by multiplying single-factor speedups. English LaTeX v0.23 unchanged.
