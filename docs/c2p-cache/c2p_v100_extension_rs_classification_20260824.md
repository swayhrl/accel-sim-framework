# V100 extension R/S classification

This table completes the paper-style R/S classification for the eight V100-generated ISPASS/Pannotia extension traces.  It is an extension dataset, not part of the canonical paper16 aggregate.

## Fixed measurement contract

- L1 latency is fixed at 20 cycles.
- `R = oracle_peer_hits / eligible_l1_misses` at L2=200; R1 iff `R >= 0.30`.
- `S = baseline_cycles(L2=200) / baseline_cycles(L2=50)`; because the trace and instruction count are fixed, this equals `IPC50 / IPC200`.  S1 iff `S >= 1.10`.
- Every input was checked for normal simulator exit, resolved L1/L2 latencies, and `oracle_cycles == baseline_cycles`.

## Results

| Workload | Oracle peer / eligible L1 miss | R | Cycles 200 / 50 | S | Group | Evidence |
|---|---:|---:|---:|---:|---|---|
| ISPASS BFS | 298,414 / 756,755 | 0.394334 | 190,739 / 168,907 | 1.129255 | R1S1 | legacy |
| ISPASS LIB | 0 / 0 | 0/0 | 2,570,260 / 1,730,168 | 1.485555 | R0†S1 | legacy |
| ISPASS LPS | 71,300 / 281,200 | 0.253556 | 99,393 / 73,903 | 1.344912 | R0S1 | legacy |
| ISPASS RAY | 0 / 2,048 | 0.000000 | 27,720 / 26,722 | 1.037348 | R0S0 | legacy |
| Pannotia ColorMax | 1,812,312 / 13,206,863 | 0.137225 | 1,705,625 / 1,705,488 | 1.000080 | R0S0 | fresh |
| Pannotia FW-block | 85,370 / 510,976 | 0.167072 | 625,892 / 599,066 | 1.044780 | R0S0 | legacy |
| Pannotia MIS | 1,101,696 / 8,109,195 | 0.135858 | 1,223,119 / 1,257,408 | 0.972730 | R0S0 | legacy |
| Pannotia PageRank | 20,041 / 30,127,217 | 0.000665 | 4,765,030 / 3,566,680 | 1.335985 | R0S1 | fresh |

`R0†` is deliberate: LIB has no eligible C2P L1 miss, hence no well-defined redundancy ratio.  It is semantically a no-sharing R0 case, but must not be silently treated as a numeric zero in a group mean.

The CSV includes the exact three source directories per workload so the raw counters and resolved configurations remain auditable.
