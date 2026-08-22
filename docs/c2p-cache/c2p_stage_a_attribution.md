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
relationship.

## Six-point C2P+ cross-check

The final diagnostic root is
`hw_run/c2p-plus-tag-port-v1-20260822/outliers/`.  All rows use backend
`b954bae8`; each control/C2P+ pair has the same copied binary, trace, and base
configuration.  The only resolved-config difference is
`-c2p_cache_separate_target_tag_port 1`.  Every completed row exited normally
and preserves `remote_hits == l2_requests_avoided`.

| Case | Control C2P cycles | C2P+ cycles | C2P+ cycle effect | Control / C2P+ L2 accesses | Control / C2P+ remote hits | Control / C2P+ target-wait timeout |
|---|---:|---:|---:|---:|---:|---:|
| Btree | 229,052 | 225,882 | -1.384% | 1,259,116 / 862,168 | 161,628 / 562,391 | 438,570 / 814 |
| ISPASS BFS | 186,246 | 177,598 | -4.643% | 987,449 / 868,733 | 87,877 / 203,447 | 129,772 / 4,493 |
| ISPASS LPS | 102,272 | 100,103 | -2.121% | — | 62,919 / 73,931 | 13,723 / 0 |
| SGEMM | 435,411 | 429,701 | -1.311% | 2,078,305 / 1,549,370 | 271,719 / 815,770 | 741,827 / 1,302 |
| 2DConvolution | 700,017 | 691,389 | -1.233% | 5,438,832 / 4,663,488 | 556,059 / 1,330,486 | 1,610,893 / 124 |
| NN | 7,224 | 7,224 | 0.000% | 16,037 / 16,037 | 0 / 0 | 0 / 0 |

NN is the strict no-op control: its two `summary.txt` files are byte-identical,
despite the named switch in the C2P+ configuration.  It verifies that a trace
without peer opportunity cannot exercise the extra target-tag path.

The high-candidate BFS result independently validates the Btree diagnosis:
C2P+ removes 96.5% of target-wait timeouts, more than doubles remote hits, and
improves cycles by 4.64%.  This is not a SGEMM/2D-specific artifact.

The two original traffic/IPC outliers separate cleanly:

- **SGEMM:** default C2P was 1.302% slower than its 429,816-cycle baseline
  despite 19.5% fewer L2 accesses.  C2P+ reaches 429,701 cycles (0.027% faster
  than that baseline), while removing 99.8% of target-wait timeouts.  Under
  this counterfactual, shared target-port contention explains essentially all
  of the observed IPC loss.
- **2DConvolution:** default C2P was 5.147% slower than its 665,750-cycle
  baseline.  C2P+ removes 99.99% of target-wait timeouts and improves the
  default point by 1.233%, but remains 3.851% slower than baseline.  Thus the
  target resource explains about 25.2% of this particular performance gap;
  the residual is genuine enabled-C2P cost.  C2P+ sends 31.7% more exact peer
  probes and has 106.4% more candidate-exhaustion fallbacks, consistent with
  Snapshot/query/probe/return work becoming visible once the target-port wait
  is removed.

LPS is the complementary low-candidate limit: it gains from the port but still
does not recover baseline IPC.  Consequently a candidate-probe budget sweep is
not the next default action.  It is warranted only if a later experiment shows
that the residual after target-port decoupling is dominated by long serial
failed-probe chains rather than by the broader enabled-C2P protocol.

No C2P+ row is eligible for a canonical paper16 aggregate or figure.  The
separate-tag port is a new, explicitly named architectural counterfactual; its
value here is causal diagnosis and a possible follow-on design point.
