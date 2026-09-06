# SpMV precomputed-triplet validation

| requirement | compact evidence | status |
| --- | --- | --- |
| one immutable payload | all modes bind `TRACE_BUNDLE_ID=d8790ea7279aa79345650ffaafc61835187d8b1e6c4b10a6e6e2cc24891db270`, the same kernelslist SHA `a3ef80aa...`, traceg-set SHA `7ff88da2...`, and source-file SHA `ca30b9fd...` | PASS |
| fixed repaired identity | Core `15cfa76e...`; Framework runtime `dc7836c4...`; runtime SHA `3e71cb...`; frozen Base/IO/OO config SHA values in the manifest | PASS |
| trace path | each mode records exactly 50 immutable `.traceg` header loads and 50 `Processing kernel` entries | PASS |
| common dynamic identity | instructions `96,963,600`; loads `722,500`; stores `18,700`; atomics and source-reachable fences both zero in all modes | PASS |
| Base drain | cycles `765,542`; PIB admit/retire `741,200/741,200`; lower acquire/release `3,859,653/3,859,653`; final PIB/lower zero | PASS |
| IO drain | cycles `658,328`; lower create/issue/response `1,329,938/1,329,938/1,329,938`; dependencies `4,518,800/4,518,800`; final inflight/PIB/lower zero | PASS |
| OO drain | cycles `638,856`; lower create/issue/response `1,323,449/1,323,449/1,323,449`; dependencies `4,518,800/4,518,800`; final inflight/PIB/active refs/lower zero | PASS |
| capture correctness boundary | source-backed hardware checker/immutable receipt is retained by `M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`; replay terminal status is kept distinct | PASS (capture evidence) |
| terminal scan | all three `/usr/bin/time` wrappers exit zero; no assertion, fatal, unclassified deadlock, or output-mismatch signature | PASS |
| classification boundary | precomputed exact triplet only; no formal registry entry, T3/T4/M5.0BT PASS, or M5.0C transition is claimed | PASS |

The Base `m4_source_completions` and `m4_observation_retires` being zero is
the documented PAPER_BASE no-sidecar behavior.  It is not a source-domain
trace discrepancy: the shared instruction/load/store/atomic/fence identity is
exact, and IO/OO each close their DTC sidecar completion/retire counters at
18,700.
