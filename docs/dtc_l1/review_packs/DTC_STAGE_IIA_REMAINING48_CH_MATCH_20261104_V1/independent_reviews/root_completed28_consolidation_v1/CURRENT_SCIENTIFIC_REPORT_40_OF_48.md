# Completed28 / fixed CORE32 interim scientific report

Frozen source as of 2026-11-04T04:07:40.482305+00:00. **40/48 new CH points accepted,0 archived simulation negatives,0 verification HOLD,8 pending.** All48 one-use identities were started; no new model is requested by this report. Complete six-cell intersection is **28/32**; all32 frozen identities remain below. The four pending programs are3MM,GESUMMV,myocyte,srad_v1, each missing its two new CH F results.

This is a completed-subset analysis, not the final32/35/42-program result. Faster-to-finish programs dominate interim coverage; completion order is not an input-selection rule. Equal program weighting in the geometric mean does not remove that coverage limitation. Final choices remain pending all48 legal terminal outcomes and independent final review.

## Exact matched statistics

S_CH=CH0/CHF; S_DH=DH0/DHF; R0=CH0/DH0; R=CHF/DHF; I=S_DH/S_CH=R/R0. Ratios above1 are positive in their stated comparison. R>1 means DH faster than CH; I>1 only means relative improvement from P0. Both F rows below use the **identical28 complete six-cell inputs**; no per-program bestF is chosen.

| Profile | Common n/32 | GM S_CH | GM S_DH | GM R0 | GM CH/DH | GM I |
| --- | --- | --- | --- | --- | --- | --- |
| F128 | 28 | 1.015488 | 1.013157 | 1.079705 | 1.077227 | 0.997705 |
| F256 | 28 | 1.022801 | 1.022166 | 1.079705 | 1.079035 | 0.999379 |

The fields below count exact integer-cycle signs, not a tolerance-based rounding of1.000. Performance regressions are accepted scientific data; they are distinct from archived failed simulations.

| Profile | Metric | Positive | Exact zero | Regression | Minimum | Median | Maximum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F128 | S_CH | 8 | 18 | 2 | 0.951367 | 1.000000 | 1.178254 |
| F128 | S_DH | 6 | 16 | 6 | 0.981743 | 1.000000 | 1.187151 |
| F128 | R | 21 | 0 | 7 | 0.723779 | 1.019376 | 3.539773 |
| F128 | I | 5 | 16 | 7 | 0.913561 | 1.000000 | 1.057515 |
| F256 | S_CH | 6 | 18 | 4 | 0.914653 | 1.000000 | 1.370455 |
| F256 | S_DH | 7 | 16 | 5 | 0.919938 | 1.000000 | 1.422263 |
| F256 | R | 21 | 0 | 7 | 0.693660 | 1.021672 | 3.608382 |
| F256 | I | 6 | 16 | 6 | 0.905203 | 1.000000 | 1.112797 |

## Suite coverage and the same matched denominators

| Suite | Common n | Frozen n | Profile | GM S_CH | GM S_DH | GM CH/DH | GM I |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CUDA Samples | 9 | 9 | F128 | 1.040091 | 1.037979 | 1.018892 | 0.997970 |
| CUDA Samples | 9 | 9 | F256 | 1.062320 | 1.059559 | 1.018311 | 0.997401 |
| Parboil | 7 | 7 | F128 | 1.002158 | 1.002002 | 1.022350 | 0.999844 |
| Parboil | 7 | 7 | F256 | 1.003420 | 1.003439 | 1.022529 | 1.000019 |
| PolyBench/GPU | 6 | 8 | F128 | 1.010296 | 1.002756 | 1.287365 | 0.992537 |
| PolyBench/GPU | 6 | 8 | F256 | 1.010599 | 1.011594 | 1.298322 | 1.000984 |
| Rodinia | 6 | 8 | F128 | 1.000000 | 1.000000 | 1.041536 | 1.000000 |
| Rodinia | 6 | 8 | F256 | 1.000000 | 1.000000 | 1.041536 | 1.000000 |

## All32 frozen inputs and exact cycles

| Program | Full input SHA | CH0 | CH128 | CH256 | DH0 | DH128 | DH256 | I128 | I256 | BothF complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlackScholes | b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0 | 8993 | 8993 | 8993 | 8971 | 8971 | 8971 | 1.000000 | 1.000000 | True |
| convolutionSeparable | 4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449 | 825151 | 702940 | 602100 | 800572 | 674364 | 562886 | 1.011325 | 1.037804 | True |
| fastWalshTransform | f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3 | 191732 | 191314 | 191430 | 185317 | 185382 | 185740 | 0.997470 | 0.996151 | True |
| histogram | 3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58 | 101432 | 101432 | 101432 | 98202 | 98202 | 98202 | 1.000000 | 1.000000 | True |
| mergeSort | dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48 | 114742 | 114742 | 114742 | 111917 | 111917 | 111917 | 1.000000 | 1.000000 | True |
| scalarProd | 2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954 | 420477 | 421185 | 422012 | 411009 | 411440 | 409181 | 1.000634 | 1.008134 | True |
| scan | 6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39 | 6710840 | 5695578 | 5273582 | 6648993 | 5748280 | 5179817 | 0.981700 | 1.008719 | True |
| transpose | 65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc | 241346 | 241346 | 241346 | 237820 | 237820 | 237820 | 1.000000 | 1.000000 | True |
| vectorAdd | e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799 | 220803 | 214503 | 223020 | 217305 | 213053 | 236217 | 0.990856 | 0.929175 | True |
| bfs | 1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0 | 4330430 | 4330430 | 4330430 | 4170294 | 4170294 | 4170294 | 1.000000 | 1.000000 | True |
| cutcp | af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8 | 4502965 | 4502965 | 4502965 | 4490473 | 4490473 | 4490473 | 1.000000 | 1.000000 | True |
| histo | 2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64 | 5636037 | 5551616 | 5502955 | 5865589 | 5789155 | 5731388 | 0.998026 | 0.999250 | True |
| mri-q | dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4 | 362244 | 362244 | 362244 | 360174 | 359855 | 359855 | 1.000886 | 1.000886 | True |
| sad | db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9 | 114310 | 114310 | 114310 | 114870 | 114870 | 114870 | 1.000000 | 1.000000 | True |
| sgemm | ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453 | 448633 | 448633 | 448633 | 409417 | 409417 | 409417 | 1.000000 | 1.000000 | True |
| stencil | c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266 | 4965921 | 4965921 | 4965921 | 4662889 | 4662889 | 4662889 | 1.000000 | 1.000000 | True |
| 2DCONV | d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0 | 1548909 | 1548909 | 1548909 | 462740 | 437573 | 429253 | 1.057515 | 1.078012 | True |
| 3DCONV | 79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d | 2958083 | 2956986 | 2958542 | 2200332 | 2205628 | 2211632 | 0.997229 | 0.995045 | True |
| 3MM | 977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d | 4191465 | MISSING | MISSING | 2402871 | 2402871 | 2402871 | MISSING | MISSING | False |
| ATAX | eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950 | 28428842 | 29882110 | 31081550 | 31880220 | 31894637 | 31321955 | 1.050644 | 1.112797 | True |
| BICG | ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef | 26298698 | 24464891 | 24651923 | 28685812 | 29210480 | 28883488 | 0.913561 | 0.930967 | True |
| GEMM | fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318 | 1395216 | 1395216 | 1395216 | 826089 | 826089 | 826089 | 1.000000 | 1.000000 | True |
| GESUMMV | 769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4 | 114860845 | MISSING | MISSING | 89502220 | 86464623 | 90151547 | MISSING | MISSING | False |
| MVT | f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079 | 26581175 | 25573002 | 24342928 | 34687540 | 35332620 | 35093446 | 0.944507 | 0.905203 | True |
| dwt2d | e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008 | 73691 | 73691 | 73691 | 73071 | 73071 | 73071 | 1.000000 | 1.000000 | True |
| gaussian | 16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3 | 763932 | 763932 | 763932 | 740717 | 740717 | 740717 | 1.000000 | 1.000000 | True |
| heartwall | 731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980 | 8782 | 8782 | 8782 | 8551 | 8551 | 8551 | 1.000000 | 1.000000 | True |
| lud | b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8 | 485866 | 485866 | 485866 | 478654 | 478654 | 478654 | 1.000000 | 1.000000 | True |
| myocyte | 977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992 | 145909578 | MISSING | MISSING | 145147976 | 145147976 | 145147976 | MISSING | MISSING | False |
| particlefilter_float | b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4 | 1861126 | 1861126 | 1861126 | 2100874 | 2100874 | 2100874 | 1.000000 | 1.000000 | True |
| particlefilter_naive | 3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e | 511136 | 511136 | 511136 | 384601 | 384601 | 384601 | 1.000000 | 1.000000 | True |
| srad_v1 | 0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4 | 8043823 | MISSING | MISSING | 7324411 | 7324411 | 7324411 | MISSING | MISSING | False |

## How to interpret the current evidence

The incomplete aggregate is descriptive. Do not promote the completed28 GM into a fixed32 conclusion, select an optimal F from this snapshot, or treat a ratio as an equal-area hardware result. Per-program extremes are retained in `CONSOLIDATION.json` for inspection, not for choosing workloads.

The reviewed first8 results retain both gains and regressions: convolutionSeparable and scan have substantial own-design downstream improvements; ATAX relative improvement includes CH regression; MVT and BICG remain absolute DH negatives under matched conditions; vectorAdd F256 regresses; GEMM/2DCONV mechanisms keep their source/profile-specific counter limits. Existing first16 mechanisms are reused at their declared scope rather than silently generalized to another profile.

New closed-program studies preserve exact zero controls and small mixed responses. fastWalshTransform has opposite small CH/DH changes; its K6 is a read-active print interval, not a proven cold-miss or request-origin class. scalarProd F256 has CH+1535cycles and DH-1828 with identical DRAM read volume; falling retries and growing MRQ tails do not prove critical-path causation. MRI-Q DH improves319cycles with K3 retaining a4cycle regression. Histo improves both designs while I remains below1 and some phases regress.3DCONV retains a CH F128 gain,CH F256 regression and both DH regressions. Stencil and cutcp have exact zero F response. particlefilter_float retains its absolute DH slowdown even though both F changes are zero.

All these case studies have independent C companion reviews in the review package. Explicit zero DRAM counts do not establish compute-bound execution. Lazy-fetch-on-read plus the frozen memcpy prefill policy can produce write misses without DRAM reads. A bank RD counter describes RD activity, not every bank state. Gauge/peak/mean values are not subtracted as cumulative events; unavailable late counters and means remain unavailable. MRQ request-to-bank assignment in core cycles is not full L2-to-DRAM service or a critical-path timer. No live progress preview contributes a cycle, speedup or completion claim here.

## Resource and scientific identity boundary

Core9eedb3131937748f0492fa83aad37d3691118d70, Framework02775fd795cde5aae1480d81cee6eb481d0a08f4,850MHz DRAM,10MiB L2, frozen input/hash/frontend identities are unchanged. FR64/128/256 couples to shared credits255/319/447. Over20 controllers F128/F256 add1280/3840 FR request slots versusP0; credit allowance is not another independent buffer to count as SRAM.

CH includes its active commonPIB256/Tag scheduling and96KiB ordinary L1 geometry. DH usesOO PIB128,512searchable logical Tags,640whole128B physical identities and finite completion service. The16KiB compatibility cache retains eligible fallback routes and cannot be deleted from area.80+16KiB is not a unified96KiB effective cache or equal area; rawordinaryL1latency20 is not proof of an identical OO hit/completion path. Physical metadata/ports/wiring/frequency/area/energy remain unquantified.

## Evidence and remaining closure

Root independent audit `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/root_independent_cycle_statistics_v1/20261104T043415364666Z` / manifest `dd5076b738679dcd262689423bbef148fe1e7b20bb2bafb4cd8700e25df1a47d` rechecks184 accepted source RESULT slots,40 accepted new raw terminal-cycle endpoints, exact signs, suite/available/common/directF statistics and actual effective-option differences. The six legal P0 wrappers are joined to their underlying accepted RESULT sources. Old144 raw lifecycles are legally reused; this audit does not claim to reopen those144 old raw logs.

Full new48 lifecycle/archive/native recovery is separately required. The CPU-qualified C/B/statistics/render waiter is already waiting for all48 source-qualified terminal outcomes; it launches no simulations and does not approve final figures, publish a final narrative or complete the Goal. Final independent end review, full fixed32 statistics, final figure inspection, scientific signoff and immutable Git/SHA readback remain pending. EnglishLaTeXv0.23 stays frozen. Next-stage conditional suggestions provide no new execution authority.
