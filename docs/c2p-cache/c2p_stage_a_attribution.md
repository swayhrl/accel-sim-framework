# C2P Stage-A transaction attribution

Status: observation-only infrastructure.  It does not alter the qualified
paper16 C2P point or any V100 extension result.

## Contract

Backend commit `49fc5df8` records cumulative per-transaction residence in
each C2P state, successful/fallback probe ordinal, the two target-timeout
causes, and the difference between the accept-time oracle peer set and the
query-time exact peer set.  The state machine, ordering, queues, and all
configuration defaults are unchanged.

The runner retains the new fields in `summary.txt`; raw `run.out`, copied
binary, resolved configuration, trace hash, and backend commit remain the
per-run provenance source.

| Measurement | Meaning | Diagnostic use |
|---|---|---|
| `residence_*_cycles` | Sum of accepted transactions' time in each state | separates Snapshot work, candidate selection, target FIFO/probe, return, and lower fallback wait |
| `remote_hit_probe_ordinal_*` | candidate ordinal at first exact remote hit | detects serial false-candidate tails before a useful hit |
| `fallback_probe_ordinal_*` | candidates attempted before lower fallback | distinguishes no-candidate traffic from long, unsuccessful scans |
| `fallback_target_*_timeout` | timeout after FIFO entry / before FIFO admission | distinguishes queue residence from unavailable target admission |
| `peer_lost/gained_before_query` | accept-time oracle versus query-time exact peer set | measures normal-cache state movement while Snapshot work is pending |

## Default-timing validation

The no-sharing NN trace was replayed with exactly the same resolved
configuration and trace on the parent backend `eff44679` and on `49fc5df8`.
The complete set of pre-existing summary fields matched exactly, including
C2P cycles (`7850`), instructions (`1,284,872`), accepted queries (`3,110`),
and every fallback/filtering/conservation counter.  The parent result is under
`hw_run/c2p-diagnosis-stage-a-v1-20260822/nn-pre-attribution/`; the attributed
result is under `hw_run/c2p-diagnosis-stage-a-v1-20260822/nn/`.

The disabled baseline is also unchanged by construction: it does not create a
C2P transaction and all C2P counters remain zero.  This is a source-level
instrumentation check, not a claim that enabled C2P must equal baseline on NN:
the enabled model still performs its intended Snapshot work before falling
back, even when no peer exists.

## Diagnostic matrix and isolation

The following root is deliberately separate from paper16 and the held V100
extension matrix:

```
hw_run/c2p-diagnosis-stage-a-v1-20260822/
```

The first paper16 replay is Btree C2P, used for high-opportunity serial-probe
attribution.  Follow-on cases are SGEMM and 2DConvolution (traffic-reduction
but IPC-loss outliers), ISPASS BFS/LPS (candidate-quality versus
protocol-cost contrast), and NN (negative control).  No row from this root is
eligible for a paper16 aggregate.

Only after this matrix identifies the dominant component will a separately
named C2P+ overlay be evaluated.  The first candidate is a bounded failed
candidate-probe budget; it must preserve one lower send or one remote fill per
transaction and `remote_hits == l2_requests_avoided`.

## First measurements and decision

| Case | Candidates/query | Hit ordinal | Target FIFO cycles/accepted | Probe cycles/accepted | Target wait timeout | Decision |
|---|---:|---:|---:|---:|---:|---|
| NN | 0.000 | — | 0.000 | 0.000 | 0 | negative control; all work falls back without a peer |
| Btree | 5.975 | 1.302 | 19.304 | 3.852 | 438,568 | target-side queue wait is the first C2P+ target |
| ISPASS BFS | 8.952 | 2.752 | 21.510 | 6.635 | 129,772 | high candidate pressure also manifests primarily as target FIFO timeout |
| ISPASS LPS | 0.926 | 1.301 | 7.705 | 4.307 | 13,723 | useful negative contrast: little candidate over-inclusion, but protocol wait remains |

The fallback ordinal is only 0.862/0.880 in Btree/BFS when averaged over all
fallbacks, including no-candidate requests.  The direct evidence therefore
does **not** justify treating a long serial false-candidate chain as the first
fix.  The bounded candidate-budget option remains an isolated experiment, but
it is not launched ahead of the more directly supported target-resource test.

`c2p-separate-target-tag-port.config` is that test.  It supplies one
pipelined remote-tag start per target per cycle, retains the existing seven
cycle remote-tag latency, and never reserves the target L1 data port.  It is a
C2P+ architectural counterfactual, not an assertion that the paper used this
exact port organization.  It is intentionally stricter than the existing
unlimited diagnostic target-port bypass.

## C2P+ separate-tag-port result

Every C2P+ point below uses backend `b954bae8`.  Its paired `control` run uses
the same binary and resolved configuration but leaves the new switch at zero.
The controls exactly reproduce the default C2P cycle, remote-hit, timeout, and
L2-access values.  Thus the deltas below are attributable to the named
counterfactual, not to the Stage-A instrumentation.

| Case | Baseline cycles | Default/control C2P cycles | Separate-tag C2P cycles | C2P+ effect | Default / C2P+ remote hits | Default / C2P+ timeout |
|---|---:|---:|---:|---:|---:|---:|
| Btree | 234,962 | 229,052 | 225,882 | −1.384% vs default C2P; −3.864% vs baseline | 161,628 / 562,391 | 438,570 / 814 |
| ISPASS LPS | 99,393 | 102,272 | 100,103 | −2.121% vs default C2P; still 0.714% slower than baseline | 62,919 / 73,931 | 13,723 / 0 |

Btree is the positive validation: target-side contention was genuinely
blocking useful remote hits (3.48x more hits and 31.5% fewer L2 accesses than
default C2P), and the more disciplined one-per-cycle tag pipe improves IPC
without using the unlimited diagnostic bypass.  LPS is the necessary limit:
the same port change removes its timeouts and improves cycles, but does not
quite recover its baseline IPC.  Its remaining cost is therefore attributable
to the broader enabled-C2P miss path (Snapshot/query/probe/return work), not
solely to the shared target data port.

This is a credible C2P+ research point, but not a replacement for the canonical
paper C2P configuration: the paper does not specify the target tag/data-port
relationship.  Next targeted evidence should cover SGEMM and 2DConvolution,
whose existing traffic/IPC contradiction motivated this diagnosis, before any
aggregate C2P+ claim.
