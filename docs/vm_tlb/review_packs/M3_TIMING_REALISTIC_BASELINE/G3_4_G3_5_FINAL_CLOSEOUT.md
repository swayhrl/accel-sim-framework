# G3-4/G3-5 final closeout — PASS

Core: `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d` (G3-4/G3-5 closeout);
accepted entry: `1b18b3c5da6e5ba22e4a03c20e3adce498311336`.  Framework handoff read
before execution: `a105fae027150a0047d23a3a5e78b9110be9c84c`.

## G3-4A — PASS

One translation page size is selected per generic run.  The existing identity
mapping, `(ASID, VPN, page-size)` keys, radix prefix classes, PWC identities,
and L1/L2 tags remain page-size aware.  New directed coverage proves exact
64KB and 2MB offsets, same-page hit / next-page miss behavior, and no
cross-class namespace collision.  Real one-kernel LUD completes for both page
sizes with four PTE requests/responses, no misassociation, and no residual VM
state.  Mixed-page policy and 4KB paging remain deliberately out of scope.

## G3-4B — PASS

The lookup state machine is `NEW -> L1 launch/service -> L2 launch/service
-> MSHR/PWQ` with generic configurable 10/80-cycle L1/L2 service values.
Each port is consumed only at its launch; a lookup in L1 or L2 service does
not re-probe.  A registered MSHR waiter bypasses before lookup arbitration; a
new UID still gets its first lookup and can then merge.  The zero-latency
setting is retained only for M2 diagnostic causality.  The exact test checks
L1 hit, L2 hit, L2 miss handoff, finite-port contention, no repeat probe/port
consumption, delayed L1 fill, new-waiter merge, and zero-latency compatibility.

## G3-5A — PASS

Requester and unique-work accounting is described in
`G3_5A_LATENCY_ACCOUNTING.md`.  All timestamps are asserted monotonic.  PTE
memory wait is per physical PTE request, and MSHR lifetime/merge depth remain
per unique translation key.  The deterministic proof covers L1, L2, PTW,
merged requester, PWC intermediate hit, and a known PTE response interval.

## G3-5B — PASS

`G3_5B_SENSITIVITY.tsv` contains the required L2-TLB (256/768/1536), MSHR
(8/32/64), walker (1/4/16), PWC (OFF/FINITE-128/IDEAL), fixed-vs-real PTW,
64KB-vs-2MB and zero-vs-nonzero lookup-timing points.  The isolated LUD trace
has only one cold translation, so capacity/MSHR/walker points are intentionally
flat; this is measured characterization, not a monotonic-performance claim.
PWC OFF removes its three cold intermediate probe cycles.  Fixed/zero
diagnostics reduce time compared with the real PTE/10-80 baseline exactly
because they remove real PTE or lookup service time.  BFS supplies the
available irregular integration: 156 L2 probes include 132 hits/24 misses,
L2 queue delay is nonzero, 17 waits merge into seven walks, and PWC saves nine
intermediate PTE requests.  No third workload is claimed available.

## Closeout invariants

- Full directed M1/M2/G3 regression: PASS.
- One-kernel M1 disabled/ideal control: same 23,977 cycles and IPC 0.8205.
- PTE conservation, physical/non-recursive requests, response association:
  PASS; see `PTE_CONSERVATION.md`.
- Replay-store-atomic and M2 conservation regressions: PASS.
- Real LUD 64KB/2MB and BFS: PASS; final MSHR/PWQ/walkers are zero.
- `git diff --check` and release build: PASS before evidence commit.

This closes reusable single-GPU M3 timing infrastructure only.  It does not
claim Segmentation paper fidelity for lookup timing, radix split or PWC, and
does not introduce M4B, sub-entry/coalescing, synthetic KV, faults, migration,
UVM, MCM or multi-ASID behavior.
