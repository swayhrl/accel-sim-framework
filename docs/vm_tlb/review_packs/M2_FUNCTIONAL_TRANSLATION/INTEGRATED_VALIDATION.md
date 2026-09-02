# M2 integrated validation and sensitivity

All replays used the cold-built RTX3070 simulator, functional mode (`2`), the
existing local traces, and `ulimit -v 10485760`; no larger-memory host was
used to establish the result.  `LUD` is the regular/coalesced and memory-path
smoke; `BFS` is the already-available irregular smoke.  No third local trace
was acquired or relabeled.

| Replay | Completion | Key end stats |
| --- | --- | --- |
| LUD full trace | normal exit | 139757 cycles, 418884 instructions; 2394 completed translations; 1 MSHR/walk/waiter; MSHR/PWQ/walkers all zero |
| BFS full trace | normal exit | 138532 cycles, 1210998 instructions; 49047 completed translations; 7 MSHR allocations/walks/waiters; MSHR/PWQ/walkers all zero |
| one-kernel G2-4 trace | normal exit | 9522 cycles, 16080 instructions; 79 completions; one allocation/start/completion/registration/wakeup; all active state zero |

## BFS sensitivity (functional mode, repaired M2-RF)

| Change from baseline | Observed end-state/result | Interpretation |
| --- | --- | --- |
| baseline: L2=768, MSHR=32, walkers=16, latency=5 | normal exit; 7 walks, 16 L2 misses, 57 pending bypasses | clean reference |
| fixed walk latency=50 | normal exit; 7 walks, 19 L2 misses, 901 pending bypasses | no wait-pollution miss explosion; 3 additional new waiters/merges from timing overlap |

The earlier L2/MSHR/walker capacity sweeps remain historical pre-RF evidence
only and are not used for the repaired counter claim.  These are sanity
observations, not calibrated performance claims.  No M3 PTE-memory timing is
inferred from them.
