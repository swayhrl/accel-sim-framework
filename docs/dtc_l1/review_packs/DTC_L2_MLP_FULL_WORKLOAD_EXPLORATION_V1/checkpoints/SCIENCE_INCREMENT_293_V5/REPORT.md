# Scientific checkpoint V5: immutable initial35 / 350 cells

Snapshot UTC 2026-10-28T00:08:52.506270+00:00 (CST08:08:52). Accepted 293 = 287 fresh strict+archive/native-restore results +6 exact P0 references. Only 14 newly accepted raw sources beyond the immutable279 anchor were opened; old279 raw records reused by RESULT SHA and UUID. Raw join covers all accepted cells, with zero identity/evidence errors; unprinted fields stay missing.

Matched DH/P0 pairs207 -> 227. Every old207 pair retains identical cycles, speedup, RESULT SHA, UUID and input/config identity. New denominator closures GESUMMV/GEMM explain most new pairs. GEMM is exactly1.0 across all8 single-factor profiles; missing DRAM counters are NOT proof of zero DRAM traffic. GESUMMV F128 improves1.035131x while F256 regresses0.992797x, so larger queues are not monotonically better. New scan E384/E768 both1.006375x and Q1280.994126x retain negative results too.

- GEMM: E384 1.000000x, E768 1.000000x, M8 1.000000x, M16 1.000000x, Q64 1.000000x, Q128 1.000000x, F128 1.000000x, F256 1.000000x
- GESUMMV: E384 1.000868x, E768 1.000868x, M8 1.000000x, M16 1.000000x, Q64 0.982493x, Q128 0.994925x, F128 1.035131x, F256 0.992797x
- scalarProd: E768 1.000000x
- scan: E384 1.006375x, E768 1.006375x, Q128 0.994126x

| Profile | Available matched inputs | Available GM | Positive/neutral/negative | Same all8 common27 GM |
|---|---:|---:|---:|---:|
| E384 | 30/35 | 1.000933 | 5/19/6 | 1.000801 |
| E768 | 29/35 | 1.000965 | 5/18/6 | 1.000801 |
| F128 | 29/35 | 1.013907 | 7/16/6 | 1.009527 |
| F256 | 29/35 | 1.021139 | 7/16/6 | 1.013141 |
| M16 | 27/35 | 1.001142 | 5/18/4 | 1.001142 |
| M8 | 28/35 | 1.000322 | 5/17/6 | 1.000546 |
| Q128 | 28/35 | 0.996405 | 4/16/8 | 0.996490 |
| Q64 | 27/35 | 0.996867 | 4/16/7 | 0.996867 |

Available populations differ and are not a profile ranking. The all8 common population expands25 -> 27; each profile on its OLD fixed population has exactly unchanged GM. Every population and suite grouping is explicit in SUPPLEMENT/SCIENTIFIC_INCREMENT. F256 common27 GM1.013141 versus available29 GM1.021139 is a population distinction. It is not evidence that old measurements changed.

DH-P0 31/35, CH-P0 33/35. Missing DH-P0: hybridsort, 3MM, SYRK, lavamd. Missing CH-P0: SYRK, lavamd. No profile has full35 accepted. No non-P0 CH matching exists, so no relative DTC/CH improvement, absolute DTC superiority or formal uniform winner is established.

Initial scan/M16-V1 remains unaccepted engineering-negative, accepted_cycles=null. Its independent supplemental V2 is excluded and cannot automatically replace that cell or enter this GM. Missing counters stay null; raw reservation rejection attempts are not unique requests or elapsed cycles; last-printed MRQ latency is not an application-wide weighted mean. FR-FCFS depth also changes F+191 partition credits. Trace completion does not prove application numerical-output correctness. No per-program best profile GM.

Read-only analysis only. Core9eedb313, Framework02775fd7, pinned binary/library, DRAM850MHz, L2 capacity/geometry/mapping, DTC/Hash,35 input identities/7UNRESOLVED, historical ledgers and Englishv0.23 unchanged. Scope excludes old72 full scan and derived models. Goal remains active; initial completion and warranted interactions/extensions plus uniform CH matching remain required.
