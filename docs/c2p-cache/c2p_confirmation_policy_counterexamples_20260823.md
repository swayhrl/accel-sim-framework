# C2P+ confirmation-policy counterexamples (pre-clean diagnostic)

> Scope note: these measurements use the superseded v1 hybrid policy. Its
> low candidate-count bins used an additional PC-hash × ordinal side table, so
> they are **not** capacity-matched PC-versus-AddrTopo results and are excluded
> from the clean v2 matrix. They remain valid evidence for where aggressive
> early stopping loses remote hits and increases fallback pressure.

Status: preliminary diagnosis from the completed `control` / `pc` / `addr`
triplets in `hw_run/c2p-confirmation-policy-v1-20260823`.  The three still
running triplets (`bicg`, `gesummv`, and Pannotia PageRank) are intentionally
not included here.  Values are final cumulative statistics from each completed
run; the strict 24-workload matrix audit remains the completion gate.

The comparison uses an exhaustive C2P+ control with the same separate target
tag pipe.  Therefore a reduction in queue wait or probe count by itself is not
an IPC benefit: it has to compensate for remote hits that now fall through to
L2.

## Facts shared by the three cases

`c2p_target_probe_port_busy_cycles` is zero in every listed configuration.
The policy does reduce target-FIFO queue residence (and, for BFS/B+tree, some
full-queue cycles), but none of these cases has an occupied target tag port.
The current predictor estimates the chance of a later peer; it does not know
whether suppressing that peer would sit on an IPC-critical L2 fallback.

| Case | PC cycle delta | Addr cycle delta | PC / Addr probe delta | PC / Addr remote-hit delta |
|---|---:|---:|---:|---:|
| `atax` | +6.88% | +3.93% | -512,915 / -186,276 | -14,558 / -8,908 |
| ISPASS `bfs` | +1.88% | +2.31% | -307,602 / -505,449 | -47,176 / -95,437 |
| `btree` | +1.12% | +1.59% | -480,275 / -501,811 | -44,002 / -66,687 |

## B+tree: directly attributable early-stop loss

The correspondence is nearly one-to-one:

| Variant | Lost remote hits | `adaptive_stop_later_peer` |
|---|---:|---:|
| PC-hash | 44,002 | 44,080 |
| AddrTopo | 66,687 | 67,435 |

Thus B+tree's IPC regression is a quality loss from ordinary per-ordinal early
stops, not a target-port or package-residual bug.  The PC package itself is
strong where it applies: 41,898 of 46,631 package starts hit, and only 1,204
package residuals still have a later exact peer.  The loss is primarily in
requests which the ordinary confirmation policy terminates before a later
exact peer.  Target-FIFO wait falls by 1.04M (PC) / 1.16M (Addr) cycles, but
that relief is not on the performance-critical path often enough to offset
the 44K / 67K L2 fallbacks.

## BFS: useful peers commonly occur late

Under exhaustive control the mean ordinal of a successful remote probe is
`746,037 / 203,447 = 3.67`.  It falls to 2.00 for PC-hash and 1.52 for
AddrTopo because late candidates are no longer reached.  The corresponding
ordinary stopped-tail counts are 93,740 and 168,772.

The four-probe package cap is also visibly material: PC has 66,787 package
misses, of which 63,661 retain a later exact peer; AddrTopo has 22,266 package
misses, of which 20,398 retain one.  This is not a conservation error: the
residual counter deliberately records exact peers beyond the hard cap.  It
means BFS is a poor match for the current fixed confirmation budget unless a
policy can identify these long, useful tails.

Although PC/Addr reduce FIFO wait by 0.83M/1.29M cycles and queue-full cycles
by 45K/76K, IPC still falls.  The evidence therefore rejects the simplistic
claim that fewer probes are automatically performance-positive for BFS.

## ATAX: timing/candidate feedback, not only directly counted early stops

ATAX's PC run loses 14,558 remote hits, but records only 2,429 ordinary
stopped tails with a later peer (Addr: 8,908 versus 3,252).  It is therefore
incorrect to attribute all of ATAX's regression to those direct stop events.
The shortened policy changes the dynamic C2P population:

| Metric | Control | PC-hash | AddrTopo |
|---|---:|---:|---:|
| Candidate total | 1,835,643 | 1,452,484 | 1,857,176 |
| No-candidate fallbacks | 17,520,359 | 17,867,005 | 17,536,041 |
| Remote-hit mean ordinal | 1.27 | 1.01 | 1.01 |
| Target-FIFO wait cycles | 1,762,629 | 1,243,410 | 1,573,823 |

Most ATAX successful probes are already first-candidate probes, so a later-hit
score cannot directly explain the full delta.  A small early-stop-induced
latency change changes warp/cache/Snapshot timing, then changes which future
requests have candidates.  The current aggregate counters establish this
feedback but cannot assign it to a particular first divergence.  This is a
model behavior to measure, not evidence of a protocol-invariant failure.

## Consequence and next observation-only step

Do not change the default policy from these aggregates alone.  Add only the
following attribution counters before trying a new decision rule:

1. `stop reason x candidate bin x ordinal x queue-pressure class`, with exact
   later-peer/no-peer partition.  The current stopped-tail counters lack the
   bin/pressure cross-product.
2. For every stopped request, `L2 fallback latency` and whether it queued
   behind a lower-memory request.  This distinguishes saved probe work from a
   critical L2 fallback without changing timing.
3. For ATAX, a candidate-availability transition counter around the first
   stopped request and subsequent Snapshot generation/epoch.  It tests the
   observed dynamic feedback rather than assuming the 14.6K lost hits all
   existed in the same static candidate population.

Only then evaluate a simple, RTL-feasible gating rule: retain exhaustive
confirmation when there is no target-queue pressure; otherwise use the same
small 64x4 score table, but compare predicted later-peer value against a
measured congestion class.  BFS must additionally prove that any longer-tail
exception repays its extra probes; simply raising the global four-probe cap is
not justified.
