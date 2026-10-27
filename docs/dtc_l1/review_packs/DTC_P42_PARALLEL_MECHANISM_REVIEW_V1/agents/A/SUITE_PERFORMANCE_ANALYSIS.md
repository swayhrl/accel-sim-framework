# Frozen 23-input suite performance and contribution analysis

Base review commit: `71584878be0c80375f9d25bcd80e171b7bf4478d`. Freeze SHA: `a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d`.

**Scope: 23 complete original four-configuration inputs, 54.76% of the 42 ordinary-program target; this is not a 42-program aggregate.** All historical failures, missing cells, zero and negative performance cases remain visible. The 18 current downstream experiments and all repair-validation runs are excluded.

## Statistical contract

Every ratio is numerator GPU model cycles divided by denominator GPU model cycles. Above one favors the denominator design. GM is equally weighted per program. Zero benefit means exactly equal accepted cycles. Runtime and performance did not select these identities. No missing value is imputed.

## Overall original panel

| Metric | N | GM | Median | Positive / zero / negative |
|---|---:|---:|---:|---:|
| CH/DH | 23 | 1.123867 | 1.027014 | 18 / 0 / 5 |
| CM/DM | 23 | 1.076346 | 1.026611 | 18 / 0 / 5 |
| DM/DH | 23 | 1.056689 | 1.000725 | 13 / 6 / 4 |
| CM/CH | 23 | 1.012009 | 1.000000 | 9 / 11 / 3 |
| relative_improvement | 23 | 1.044150 | 1.000000 | 11 / 6 / 6 |

## Suite coverage and comparisons

| Suite | Complete / target | Frozen / unresolved | CH/DH GM (median; +/0/−) | CM/DM GM | DM/DH GM | CM/CH GM |
|---|---:|---:|---:|---:|---:|---:|
| PolyBench/GPU | 7/9 (77.78%) | 9/0 | 1.353126 (1.344380; 4/0/3) | 1.160490 | 1.209685 | 1.037470 |
| Rodinia | 7/17 (41.18%) | 10/7 | 1.049451 (1.027014; 6/0/1) | 1.058323 | 0.993191 | 1.001587 |
| CUDA Samples | 6/9 (66.67%) | 9/0 | 1.023391 (1.027972; 6/0/0) | 1.023368 | 0.995763 | 0.995741 |
| Parboil | 3/7 (42.86%) | 7/0 | 1.031250 (1.005747; 2/0/1) | 1.039032 | 1.003012 | 1.010581 |

All four metrics have identical within-suite members. JSON provides all four medians, signs, ranges, program membership and per-cell evidence. The overall GM weights 23 programs equally; it is not the equal mean of four suite GMs.

## Full per-program performance and log-GM contribution

| Program | Suite | CH/DH | CM/DM | DM/DH | CM/CH | CH/DH net-log contribution | Leave-one-out CH/DH GM |
|---|---|---:|---:|---:|---:|---:|---:|
| 2DCONV | PolyBench/GPU | 3.347255 | 3.314588 | 1.016608 | 1.006686 | 44.98% | 1.069475 |
| 3DCONV | PolyBench/GPU | 1.344380 | 1.323365 | 1.015880 | 1.000000 | 11.02% | 1.114752 |
| 3MM | PolyBench/GPU | 1.744357 | 1.462780 | 1.313668 | 1.101613 | 20.72% | 1.101632 |
| ATAX | PolyBench/GPU | 0.891739 | 0.763661 | 1.272575 | 1.089798 | -4.27% | 1.135748 |
| BICG | PolyBench/GPU | 0.916784 | 0.616013 | 1.434765 | 0.964059 | -3.23% | 1.134319 |
| BlackScholes | CUDA Samples | 1.002452 | 1.002452 | 1.000000 | 1.000000 | 0.09% | 1.129722 |
| convolutionSeparable | CUDA Samples | 1.030702 | 1.028560 | 0.965618 | 0.963612 | 1.13% | 1.128296 |
| dwt2d | Rodinia | 1.008485 | 1.008485 | 1.000000 | 1.000000 | 0.31% | 1.129414 |
| fastWalshTransform | CUDA Samples | 1.034616 | 1.026611 | 1.007797 | 1.000000 | 1.27% | 1.128102 |
| gaussian | Rodinia | 1.031341 | 1.031341 | 1.000000 | 1.000000 | 1.15% | 1.128264 |
| GEMM | PolyBench/GPU | 1.688942 | 1.410609 | 1.296961 | 1.083225 | 19.51% | 1.103250 |
| heartwall | Rodinia | 1.027014 | 1.027014 | 1.000000 | 1.000000 | 0.99% | 1.128480 |
| histogram | CUDA Samples | 1.032891 | 1.037382 | 1.002719 | 1.007079 | 1.20% | 1.128187 |
| lud | Rodinia | 1.015067 | 1.014823 | 1.000240 | 1.000000 | 0.56% | 1.129080 |
| mergeSort | CUDA Samples | 1.025242 | 1.025242 | 1.000000 | 1.000000 | 0.93% | 1.128569 |
| mri-q | Parboil | 1.005747 | 1.000707 | 1.005036 | 1.000000 | 0.21% | 1.129554 |
| MVT | PolyBench/GPU | 0.766303 | 0.665740 | 1.179869 | 1.025033 | -9.91% | 1.143601 |
| particlefilter_float | Rodinia | 0.885882 | 0.929277 | 0.952377 | 0.999030 | -4.51% | 1.136088 |
| particlefilter_naive | Rodinia | 1.329003 | 1.329003 | 1.000000 | 1.000000 | 10.59% | 1.115335 |
| sad | Parboil | 0.995125 | 0.995844 | 0.999277 | 1.000000 | -0.18% | 1.130099 |
| sgemm | Parboil | 1.095785 | 1.125612 | 1.004731 | 1.032080 | 3.41% | 1.125160 |
| srad_v1 | Rodinia | 1.098221 | 1.110754 | 1.000725 | 1.012145 | 3.49% | 1.125047 |
| transpose | CUDA Samples | 1.014826 | 1.020296 | 0.999029 | 1.004413 | 0.55% | 1.129093 |

Contribution is log(ratio)/sum(log(ratios)), not a share of saved wall time. Negative contributions offset positives; percentages can exceed 100%. Full input digests and four accepted cycles are in the identity appendix below and JSON.

## High-gain cases and concentration

- **2DCONV:** CH/DH=3.347255 while CM/DM=3.314588. The DTC gain exists before Hash; DTC Hash adds only 1.6608%, conventional Hash 0.6686%, and relative advantage improves 0.9856%. This ratio evidence rules out attributing its whole 3.35x gain to Hash, but cannot identify a particular DTC mechanism.
- **3DCONV:** CH/DH=1.344380, CM/DM=1.323365, DM/DH=1.015880 and CM/CH=1. Its main observed benefit likewise precedes Hash.
- **3MM/GEMM:** DTC Hash improves 1.313668x/1.296961x, compared with conventional Hash 1.101613x/1.083225x. Relative DTC advantage improves 1.192495x/1.197314x. Mapping sensitivity contributes appreciably, while pre-Hash DTC gains of 1.462780x/1.410609x also remain.
- **particlefilter_naive:** CM=CH and DM=DH exactly, with CH/DH=CM/DM=1.329003. Hash contributes no cycle change in this frozen input; the remaining design differences require separate causal evidence.

These are arithmetic decompositions, not isolated causal interventions on the full design. Counter/source attribution belongs to Agent C.

The five named cases supply **106.82% of the net CH/DH log gain**, or **87.48% of positive log gain before negative cases**. The other 18 have CH/DH GM **0.989876**, median **1.014947**, with 13 positive and 5 negative cases. The formal panel remains all 23.

## Diagnostic sensitivity (never an alternative selected main set)

| Sensitivity | N | CH/DH GM | CM/DM GM | DM/DH GM | CM/CH GM |
|---|---:|---:|---:|---:|---:|
| all_23_FORMAL_FROZEN_PANEL | 23 | 1.123867 | 1.076346 | 1.056689 | 1.012009 |
| leave_out_2DCONV_DIAGNOSTIC_ONLY | 22 | 1.069475 | 1.022700 | 1.058548 | 1.012252 |
| leave_out_named_high_five_DIAGNOSTIC_ONLY | 18 | 0.989876 | 0.956787 | 1.039838 | 1.005078 |
| leave_out_particlefilter_float_exact_build_sensitivity_ONLY | 22 | 1.136088 | 1.083558 | 1.061693 | 1.012603 |

The particlefilter_float diagnostic preserves the published 22 same-exact-build sensitivity; it does not justify dropping an unfavorable benchmark. All 23 leave-one-out results and contributions for every metric are in JSON.

## Negative cases and small gains

Five CH/DH negative cases are retained: MVT 0.766303, particlefilter_float 0.885882, ATAX 0.891739, BICG 0.916784, and sad 0.995125. ATAX/MVT/BICG improve with DTC Hash but remain slower than their matched CH design. A better relative response to Hash is not the same as DTC beating CH.

Most remaining gains are small: BlackScholes 0.245%, mri-q 0.575%, dwt2d 0.848%; lud/transpose approximately1.5%; mergeSort/heartwall approximately2.5–2.7%; convolutionSeparable/histogram/fastWalshTransform approximately3.1–3.5%; sgemm/srad approximately9.6–9.8%. Ratios alone do not establish a mechanism or meaningful real-hardware significance. Hash changes both designs by almost nothing for several of these. No equivalence or reproducibility error bars are inferred from one deterministic model run.

## Missingness and selection bias

There are 35 frozen identities, of which 12 lack an original accepted complete four-cell result, plus seven unresolved identities. The 140 selected cells contain111 accepted originals. Missingness is tied to telemetry-closure, resource/guard, receipt, admission and pending status; source-version ambiguity excludes seven programs. This is an availability-conditioned panel, not a random sample. The direction or magnitude of its bias cannot be estimated without the missing legal evidence. Do not extrapolate 1.123867x to42 programs, and do not convert a failure into a slowdown or neutral result.

| Missing program | Identity | Four cell states CM / CH / DM / DH |
|---|---|---|
| backprop | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| bfs | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE |
| cfd | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| cutcp | IDENTITY_FROZEN | NOT_ADMITTED / NOT_ADMITTED / NOT_ADMITTED / NOT_ADMITTED |
| GESUMMV | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE / ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL |
| histo | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE |
| hybridsort | IDENTITY_FROZEN | ORIGINAL_RECEIPT_MISSING / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE |
| kmeans | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| lavamd | IDENTITY_FROZEN | ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE |
| myocyte | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE / ORIGINAL_NEGATIVE / ACCEPTED_ORIGINAL |
| nn | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| nw | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| pathfinder | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| scalarProd | IDENTITY_FROZEN | ORIGINAL_NEGATIVE / ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE |
| scan | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE / ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL |
| stencil | IDENTITY_FROZEN | ORIGINAL_NEGATIVE / ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE |
| streamcluster | UNRESOLVED | NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY / NO_SELECTED_IDENTITY |
| SYRK | IDENTITY_FROZEN | PENDING_OR_NOT_DONE / ORIGINAL_NEGATIVE / PENDING_OR_NOT_DONE / ORIGINAL_NEGATIVE |
| vectorAdd | IDENTITY_FROZEN | ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ACCEPTED_ORIGINAL / ORIGINAL_NEGATIVE |

## Identity and evidence appendix

Every row below maps to `programs[i].cells[CM|CH|DM|DH]` in SUITE_PERFORMANCE_ANALYSIS.json, containing actual Core/Framework/binary identities; all four configuration path/SHA records and resolved options; cohort/UUID; accepted-result, strict, DONE and archive receipt paths/SHA; raw compressed/uncompressed SHA; original kernel counter locations; 164 archive and native restore receipt. Historical declared spec builds are stored separately from actual strict/launch builds. Some authorized observational cap-only rebinds retain an older spec declaration; that is not the actual binary identity.

| Program | Full input digest | CM cycles | CH cycles | DM cycles | DH cycles |
|---|---|---:|---:|---:|---:|
| 2DCONV | `d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0` | 1559265 | 1548909 | 470425 | 462740 |
| 3DCONV | `79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d` | 2958083 | 2958083 | 2235274 | 2200332 |
| 3MM | `977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d` | 4617374 | 4191465 | 3156575 | 2402871 |
| ATAX | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` | 30981690 | 28428842 | 40569964 | 31880220 |
| BICG | `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef` | 25353488 | 26298698 | 41157397 | 28685812 |
| BlackScholes | `b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0` | 8993 | 8993 | 8971 | 8971 |
| convolutionSeparable | `4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449` | 795125 | 825151 | 773047 | 800572 |
| dwt2d | `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008` | 73691 | 73691 | 73071 | 73071 |
| fastWalshTransform | `f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3` | 191732 | 191732 | 186762 | 185317 |
| gaussian | `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3` | 763932 | 763932 | 740717 | 740717 |
| GEMM | `fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318` | 1511333 | 1395216 | 1071405 | 826089 |
| heartwall | `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980` | 8782 | 8782 | 8551 | 8551 |
| histogram | `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58` | 102150 | 101432 | 98469 | 98202 |
| lud | `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8` | 485866 | 485866 | 478769 | 478654 |
| mergeSort | `dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48` | 114742 | 114742 | 111917 | 111917 |
| mri-q | `dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4` | 362244 | 362244 | 361988 | 360174 |
| MVT | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | 27246579 | 26581175 | 40926747 | 34687540 |
| particlefilter_float | `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4` | 1859320 | 1861126 | 2000825 | 2100874 |
| particlefilter_naive | `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e` | 511136 | 511136 | 384601 | 384601 |
| sad | `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9` | 114310 | 114310 | 114787 | 114870 |
| sgemm | `ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453` | 463025 | 448633 | 411354 | 409417 |
| srad_v1 | `0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4` | 8141513 | 8043823 | 7329720 | 7324411 |
| transpose | `65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc` | 242411 | 241346 | 237589 | 237820 |

## Limits and reproducibility

- This freeze selects content-defined trace identities. Exact capture-time executable/original input and complete application certification are not newly granted for all members. Published statistics are conditional on recorded trace contracts; do not relabel as a fully certified42-application paper aggregate.
- Complete-case availability is not random: failures, telemetry closure/resource-policy failures, pending runs and unresolved source versions are missing. No inference to the 42-program population or to workloads in general.
- Observational Framework cap-only equivalence is inherited from MODEL_COMPARABILITY; particlefilter_float crosses the two Framework/binary variants. Exact-build sensitivity is diagnostic, never silently removes this negative case.
- Traditional96KiB/768lines versus DTC80KiB/640physical128B lines/512logicalTags, different PIB/finite-service structures and timing mean this is not area/capacity matched. Same Hash family does not make the whole designs matched.
- Ratios identify behavior, not hardware causation. Other agents audit counter semantics and microarchitectural attribution; no dominant mechanism is asserted from ratios alone.

Reproduce: `python analyze_suite.py --input-dir <directory_with_the_four_hashed_snapshots> --output-dir <independent_output_directory>`. Plot dependencies must already be available; the script does not install packages. All file input SHA and the baseline commit are recorded in JSON. This analysis reads local closed snapshots only, scans no trace and starts no model. English manuscript v0.23 is unchanged.

Figures: `performance_by_suite.png/.svg`, `log_gain_contributions.png/.svg`, and `coverage.png/.svg`. Labels and captions explicitly identify23 complete original inputs, retain negative cases and distinguish diagnostic exclusions.
