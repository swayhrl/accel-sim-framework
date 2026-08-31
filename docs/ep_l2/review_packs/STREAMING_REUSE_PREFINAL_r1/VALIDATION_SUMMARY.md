# Validation summary

All evidence below is preserved under `/workspace/results/ep_l2_streaming_reuse/`.

| Gate | Result | Evidence |
| --- | --- | --- |
| Directed sector contract | PASS | `EPL2SRV1 directed contract: PASS` |
| Directed sector parser regression | PASS | `EPL2SRV1 parser regression: PASS` |
| Motivation contract/parser regression | PASS | `EPL2MOTV1 directed contract: PASS`; `EPL2MOTV1 parser regression: PASS` |
| Final-snapshot parser repair | PASS | `parser_repair_probe_sector_sad/`: 256 app snapshots, 192 superseded; final cumulative snapshots parse and close. |
| Release build | PASS | `build_core.log`, `build_framework_r2.log`; provenance Core `ca3e7…`, Framework `db1c…`. |
| OFF/ON timing neutrality | PASS | Three r4 workloads have identical terminal cycles, instructions, and digest; ON changes only observation counters. |
| Motivation output preservation under ON | PASS | For vectorAdd_4M, convolutionSeparable, and sad, all seven Motivation r1 CSV products match OFF exactly. |

Timing-neutrality details:

| Workload | Terminal cycles | Instructions | Digest equal | OFF events / bytes | ON events / bytes |
| --- | ---: | ---: | --- | ---: | ---: |
| vectorAdd_4M | 73,873 | 56,000,000 | yes | 266.91 / 552,960 | 283.51 / 679,936 |
| convolutionSeparable | 292,211 | 714,547,200 | yes | 1247.47 / 933,888 | 1455.15 / 1,126,400 |
| sad | 110,653 | 157,583,646 | yes | 184.30 / 925,696 | 207.01 / 962,560 |

Earlier runner/parser failures remain preserved as diagnostic evidence. Only runner/parser code was repaired; accepted data were re-frozen with the runtime candidate stated in `README.md`.

