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

## BFS sensitivity (functional mode)

| Change from baseline | Observed end-state/result | Interpretation |
| --- | --- | --- |
| baseline: L2=768, MSHR=32, walkers=16, latency=5 | 138532 cycles; 7 walks; 42 L2 misses | reference only |
| L2 entries=1 | normal exit; 57 walks, 339 L2 misses, 56 L2 evictions, 63 registrations/wakeups | finite L2 capacity changes translation activity as expected |
| MSHR entries=1 | normal exit; same 7 walks and zero full events | this trace did not saturate MSHRs; directed G2-2 proves the full path |
| walkers=1 | normal exit; same 7 walks | this trace did not overlap enough walks; directed G2-3 proves saturation/queueing |
| fixed walk latency=50 | normal exit; 138727 cycles; 7 walks, 8 registrations/wakeups, 357 L2 misses | timing parameter affects the replayed functional path without loss/deadlock |

These are sanity observations, not calibrated performance claims.  No strict
IPC monotonicity is asserted, and no M3 PTE-memory timing is inferred from
them.
