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
