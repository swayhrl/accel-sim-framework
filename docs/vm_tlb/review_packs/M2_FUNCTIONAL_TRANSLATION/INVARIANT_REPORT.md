# M2 conservation and invariant report

Status: `PASS`.  The test suite asserts the model invariants; end statistics
from real replays check that they remain true at quiescence.

| Invariant | Directed proof | Real replay observation |
| --- | --- | --- |
| One active walk per `(ASID, VPN, page-size)` key | G2-2 same-key merge/replay test | LUD: 1 allocation/1 start/1 completion; BFS: 7/7/7 |
| Finite MSHR/PWQ/walker backpressure | G2-2 one-entry MSHR and G2-3 PWQ/walker pressure tests | Functional traces end with MSHR=PWQ=walkers=0 |
| Allocations equal releases at quiescence | G2-2 invariant test | LUD 1 active->0; BFS 7 active->0 |
| Registrations equal successful wakeups | G2-2/G2-3 invariant tests | LUD 1=1; BFS 7=7 |
| Walk starts equal completions | G2-3 invariant test | LUD 1=1; BFS 7=7 |
| No untranslated data request enters the data path | G2-1 source gate plus G2-4 pending/replay test | real functional replay terminates normally |
| No duplicate store/atomic effect | G2-4 exact-once tests | no duplicate-side-effect diagnostic in real runs |
| No PTE-memory traffic in repaired M2 execution | fixed-latency walker design and directed suite | the source contains the provisional `pte_request` class, but the M2 execution path emits no PTE memory traffic |
| Registered waiter cannot monopolize TLB ports | RF pending-retry test: 9 bypasses, zero added L1/L2 probes/stalls; B uses sole L2 port | BFS latency 50: 901 bypasses, 156 L2 probes, no loss/starvation |
| Kernel-boundary TLB persistence | RF focused warm-boundary test plus `gpgpu_sim` lifetime source proof | controller is constructed once and not reset by ordinary init/done paths |

The resource sweeps are supplementary sanity checks.  They are not used to
replace the directed saturation proofs: the existing BFS trace did not exert
MSHR or walker capacity pressure at the tested baseline, so reducing either
to one did not change its final aggregate counters.  In contrast, reducing
L2 entries to one increased walks to 57 and L2 evictions to 56, while raising
fixed walk latency to 50 increased walk-related activity.  All sweeps reached
quiescence without loss or duplicate wakeup.
