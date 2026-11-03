# Final Stage II-A first16 CH matching: fixed first8 subset

B snapshot 2026-11-03T23:42:38.000055+00:00; acceptedCH 16/16; archivednegativeCH 0/16. Root verified science execution complete. This is the predeclared first8 subset, not core32/full35 coverage or authorization for remaining48.

## Six-cycle comparison

| Program | Input digest | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
|---|---|---:|---:|---:|---:|---:|---:|
| convolutionSeparable | 4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449 | 825151 | 702940 | 602100 | 800572 | 674364 | 562886 |
| scan | 6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39 | 6710840 | 5695578 | 5273582 | 6648993 | 5748280 | 5179817 |
| 2DCONV | d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0 | 1548909 | 1548909 | 1548909 | 462740 | 437573 | 429253 |
| ATAX | eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950 | 28428842 | 29882110 | 31081550 | 31880220 | 31894637 | 31321955 |
| MVT | f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079 | 26581175 | 25573002 | 24342928 | 34687540 | 35332620 | 35093446 |
| BICG | ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef | 26298698 | 24464891 | 24651923 | 28685812 | 29210480 | 28883488 |
| vectorAdd | e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799 | 220803 | 214503 | 223020 | 217305 | 213053 | 236217 |
| GEMM | fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318 | 1395216 | 1395216 | 1395216 | 826089 | 826089 | 826089 |

Cycle values are whole accepted replay cycles. Null/new negative cells are not zeros and remain in the fixed8 matrix. Full input/member SHA and32 old/16 new source paths are in FULL_SHA_REFERENCES.json.

## Per-input matching

| Program | F | Status | S_CH=CH0/CHF | S_DH=DH0/DHF | R=CHF/DHF | I=S_DH/S_CH |
|---|---|---|---:|---:|---:|---:|
| convolutionSeparable | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.173856944 | 1.187151153 | 1.042374741 | 1.011325238 |
| convolutionSeparable | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.370455074 | 1.422263123 | 1.069665971 | 1.037803537 |
| scan | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.178254428 | 1.156692611 | 0.990831692 | 0.981700202 |
| scan | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.272539234 | 1.283634731 | 1.018101991 | 1.008719178 |
| 2DCONV | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.000000000 | 1.057514975 | 3.539772792 | 1.057514975 |
| 2DCONV | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.000000000 | 1.078012268 | 3.608382469 | 1.078012268 |
| ATAX | F128 | ACCEPTED_MATCHED_QUADRUPLE | 0.951366620 | 0.999547980 | 0.936900771 | 1.050644367 |
| ATAX | F256 | ACCEPTED_MATCHED_QUADRUPLE | 0.914653291 | 1.017823440 | 0.992324713 | 1.112797002 |
| MVT | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.039423334 | 0.981742650 | 0.723778820 | 0.944507034 |
| MVT | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.091946499 | 0.988433567 | 0.693660235 | 0.905203293 |
| BICG | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.074956680 | 0.982038364 | 0.837538137 | 0.913560874 |
| BICG | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.066801077 | 0.993156090 | 0.853495360 | 0.930966524 |
| vectorAdd | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.029370219 | 1.019957475 | 1.006805818 | 0.990855823 |
| vectorAdd | F256 | ACCEPTED_MATCHED_QUADRUPLE | 0.990059188 | 0.919938023 | 0.944131879 | 0.929174775 |
| GEMM | F128 | ACCEPTED_MATCHED_QUADRUPLE | 1.000000000 | 1.000000000 | 1.688941506 | 1.000000000 |
| GEMM | F256 | ACCEPTED_MATCHED_QUADRUPLE | 1.000000000 | 1.000000000 | 1.688941506 | 1.000000000 |

All signs and exact-zero cases remain. I>1 means the relative change favoursDH; both designs can be slower thanP0. R>1, separately, means DH has fewer cycles thanCH. Neither proves equal area.

## Same-population summary

F128/F256 common accepted input count 8/8. Primary GM and directF comparisons below use precisely this same population. Per-F available sets are preserved separately in STATISTICS.json and must not be compared as if their denominators match.

| F | Metric | n/8 | GM | Positive | Negative | Exactzero | Missing |
|---|---|---|---:|---:|---:|---:|---:|
| F128 | S_CH | 8/8 | 1.053160710 | 5 | 1 | 2 | 0 |
| F128 | S_DH | 8/8 | 1.045478946 | 4 | 3 | 1 | 0 |
| F128 | R | 8/8 | 1.170800616 | 4 | 4 | 0 | 0 |
| F128 | I | 8/8 | 0.992705991 | 3 | 4 | 1 | 0 |
| F128 | R_P0 | 8/8 | 1.179403194 | 5 | 3 | 0 | 0 |
| F256 | S_CH | 8/8 | 1.079176069 | 4 | 2 | 2 | 0 |
| F256 | S_DH | 8/8 | 1.076911812 | 4 | 3 | 1 | 0 |
| F256 | R | 8/8 | 1.176928647 | 4 | 4 | 0 | 0 |
| F256 | I | 8/8 | 0.997901865 | 4 | 3 | 1 | 0 |
| F256 | R_P0 | 8/8 | 1.179403194 | 5 | 3 | 0 | 0 |

Sign counts compare exact integer-rational ratios to1, without floatepsilon; exact numerator/denominator is retained per input. Zero response never fills a missing value.

| Direct same-set comparison | n/8 | GM | Positive | Negative | Exactzero | Missing |
|---|---|---:|---:|---:|---:|---:|
| CH_F128_over_F256 | 8/8 | 1.024702174 | 3 | 3 | 2 | 0 |
| DH_F128_over_F256 | 8/8 | 1.030065519 | 6 | 1 | 1 | 0 |
| I_F256_over_F128 | 8/8 | 1.005234052 | 5 | 2 | 1 | 0 |

CH_F128/F256 andDH_F128/F256 >1 meanF256 is faster. I_F256/I_F128 >1 favours the relativeDH change atF256. No per-program winner is spliced into a uniformGM.

## Suite groups on the same common inputs

| Suite | F | Metric | n/expected | GM | Positive | Negative | Exactzero | Missing |
|---|---|---|---|---:|---:|---:|---:|---:|
| CUDA Samples | F128 | S_CH | 3/3 | 1.124972616 | 3 | 0 | 0 | 0 |
| CUDA Samples | F128 | S_DH | 3/3 | 1.118841796 | 3 | 0 | 0 | 0 |
| CUDA Samples | F128 | R | 3/3 | 1.013109750 | 2 | 1 | 0 | 0 |
| CUDA Samples | F128 | I | 3/3 | 0.994550249 | 1 | 2 | 0 | 0 |
| CUDA Samples | F256 | S_CH | 3/3 | 1.199680816 | 2 | 1 | 0 | 0 |
| CUDA Samples | F256 | S_DH | 3/3 | 1.188666417 | 2 | 1 | 0 | 0 |
| CUDA Samples | F256 | R | 3/3 | 1.009308761 | 2 | 1 | 0 | 0 |
| CUDA Samples | F256 | I | 3/3 | 0.990818892 | 2 | 1 | 0 | 0 |
| PolyBench/GPU | F128 | S_CH | 5/5 | 1.012293077 | 2 | 1 | 2 | 0 |
| PolyBench/GPU | F128 | S_DH | 5/5 | 1.003790906 | 1 | 3 | 1 | 0 |
| PolyBench/GPU | F128 | R | 5/5 | 1.276964461 | 2 | 3 | 0 | 0 |
| PolyBench/GPU | F128 | I | 5/5 | 0.991601078 | 2 | 2 | 1 | 0 |
| PolyBench/GPU | F256 | S_CH | 5/5 | 1.012764014 | 2 | 1 | 2 | 0 |
| PolyBench/GPU | F256 | S_DH | 5/5 | 1.014967718 | 2 | 2 | 1 | 0 |
| PolyBench/GPU | F256 | R | 5/5 | 1.290582550 | 2 | 3 | 0 | 0 |
| PolyBench/GPU | F256 | I | 5/5 | 1.002175931 | 2 | 2 | 1 | 0 |

Suite directF and per-F available statistics are retained in STATISTICS.json. The first8 comprise only their declared suites; no Rodinia/Parboil or whole35 inference follows.

## Scientific and hardware boundaries

FR-FCFS64→128/256 also raises sharedcredits255→319/447 per controller. L2 remains10MiB, MSHR192×4, missQ32 and DRAM850MHz. Fixed within-design L1/Hash/Tag/PIB and completion service are preserved. CH PAPER_BASE commonPIB256 and Tag scheduling are active; DH PAPER_OO PIB128 is active. Raw DHcommonPIB8 anddtcMSHR32 are not OO active capacities. Declared geometry, active paths and physical area differ; no equal-area, frequency, energy or implementation-free expansion claim. Resource-cost source SHA and line evidence is linked in PROVENANCE.json.

The existing replay policy enables gpgpu_perf_sim_memcpy1 and flush_l2_cache0: HtoD command handling directly updates L2 tags rather than issuing ordinary timed DRAM requests. This is a matched initial-state policy, not a claim all copied lines remain resident. GEMM3MiB copy and2DCONV64MiB copy do not justify equal residency;64MiB exceeds10MiB. Source/capture ELF and original numeric-state binding remain uncertified; strict replay termination does not certify native application numerical correctness. Frozen input identity is unchanged.

Traffic/blockage counter associations do not isolate L2-to-DRAM queue waiting or a sole causal bottleneck. Last printed strict metrics mix scopes; per-kernel endpoint/delta proof is needed before causal attribution. Static address repetition is not observed cachehit/MSHRmerge; missing counters remain unknown. These performance observations neither estimate unfinished cycles nor repair numeric semantics.

## Reproduction

STATISTICS.json retains wide cycles, every input/Fmetric, exact ratio components, same-set GM/sign/missing populations and suite groups. FULL_SHA_REFERENCES.json retains input/full member SHA and source paths. Figures use the unchanged SHA-pinned9d plotting source. No simulation/registration/owner/history/manuscript operation is present in this generator. Remaining48 batching is not designed or released by this report.
