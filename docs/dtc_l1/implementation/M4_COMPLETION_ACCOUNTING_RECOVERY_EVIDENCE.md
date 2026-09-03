# M4 completion-accounting recovery evidence

Status: **R4C.0--R4C.7 PASS -- M4 resumed**.

## Provenance

- Core recovery base: `bfb3b6337f2210cde99d323e2bd42ec4e9775b79`.
- Core recovery result: `a33ffa87ed4d31d9725b693ea4f822ad1ed1c330`.
- Framework recovery base: `83b63d409c8699348cebe7be019648cdfedd67c7`.
- Workload repository: `gpgpu-workloads` at
  `de9cf4293f418877aa9cdb6a2395338ca06674a6`.
- Workload is the recorded local
  `suites/polybench-gpu-wrapper/pb_2dconv`, binary `pb_2dconv`, extracted PTX
  `pb_2dconv.1.sm_52.ptx`; no source, input, PTX, or unrelated simulator
  option was changed.  Only the mode configuration differs.

## R4C.0--R4C.2: localization and classification

The pre-repair bounded trace deterministically found the first failure at
`cycle=7703`, `SM=0`, `UID=15888`, `PC=0x148`, destination register `20`.
It registered and PIB-owned two unique 128B references, then attempted a
second close when pending writes were already zero.  The first PIB entered at
cycle 7701 with the original instruction still carrying `accessq=5`; after
the first retirement at cycle 7702 that same unconsumed dispatch instruction
re-entered the IO memory path and recreated the PIB.

The compact pending-write provenance is decisive:

```text
cycle 7700: UID 15888 reg 20, 0 + 2 = 2, ISSUE_REGISTER
cycle 7702: UID 15888 reg 20, 2 - 2 = 0, DTC_IO_COMPLETE
cycle 7703: duplicate DTC IO completion, pending=0, dependencies=2
```

The ledger additionally recorded `registered=2`, `pib=2`, `closed=2` before
the repeated PIB creation.  Therefore this is **Category C -- duplicate DTC
completion**, not a conventional decrement, cardinality divergence, or
cross-instruction register alias.  The R4C.0 diagnostic captures the
issue/PIB reference vectors (128B addresses and masks), classification,
outputs, access-queue state, and bounded mutation history; the raw traces are
retained at `/tmp/dtc-r4c0-flow-5HjIi4/run.log` and
`/tmp/dtc-r4c12-Zhj2O7/run.log`.

## R4C.3--R4C.4: repair and permanent checks

The minimal source repair preserves the frozen 128B dependency granularity:

- IO may retire its head only after `next_reference == references.size()`;
- OO similarly excludes a cacheable entry until all of its references are
  admitted;
- the completion path consumes the dependency count registered at issue,
  after asserting equality with the PIB-owned count;
- a production `completion_accounting` lifecycle enforces
  `REGISTERED -> PIB_OWNED -> READY -> CLOSED` and rejects a second close;
- terminal statistics assert no live cacheable DTC ledger entry remains.

The pre-existing `pending >= dependencies`, exact-zero pending, and scoreboard
release assertions remain present and are not weakened.  A checker-only
READY retry assertion found during the first post-change run was source
resolved: shared operand-collector backpressure can retry a ready observation.
The non-retryable ledger READY transition now occurs only after a successful
writeback grant; this changes no functional cache, NoC, Tag, or scoreboard
behavior.

`dtc_l1_completion_accounting_test` exercises the production accounting class:

- C01 exact cardinalities 1/2/4/32;
- C02 four sector accesses grouped into one 128B dependency;
- C03 duplicate close must terminate the child with `SIGABRT`.

C04 is source-backed: `memory_cycle` routes eligible IO/OO loads before the
conventional L1D route, and response FIFO ownership calls the IO/OO consumers
before any conventional fill.  C05 is source-backed: the scheduler invokes
`Scoreboard::checkCollision`, and `reserveRegister` rejects re-reserving the
same warp/register before the DTC completion's single release.

Final Core release build and all CTests passed:

```text
dtc_l1_m1_common_test                 PASS
dtc_l1_bad_generation_test            PASS
dtc_l1_completion_accounting_test     PASS
```

## R4C.5: final-source 2DConv validation

Both runs use Core `a33ffa87`; the runtime `libcudart.so` SHA-256 is
`0bc9fd90949bbd0c9df475c015e880a38e453f1e1fde5ec45c87d14de22c94a7`.

| Mode | Config SHA-256 | Result | Accounting closeout | Log SHA-256 |
| --- | --- | --- | --- | --- |
| PAPER_IO | `43d87dbd6e971d882ac7c1375126517d32679178196667ef26fbee3006eb6610` | PASS, 293 s, output mismatches 0 | lower `1580/1580/1580`, inflight/PIB/credits `0`, dependencies `6804/6804`, conventional MSHR full `0/0` | `45c9d61f865d0497b3232a0f95501fef9ee1927aaf61c4472b4f1dfa4a8eee61` |
| PAPER_OO | `3bfc63db580f89b3ed7e845e175f3593a6d76b12ce200623a84390e178061b44` | PASS, 241 s, output mismatches 0 | lower `1580/1580/1580`, inflight/PIB/active refs/credits `0`, dependencies `6804/6804` | `68317e11c37878c01b38572c2cb3a1d9fd266526d93671715e9e6e67e0ad41d5` |

No pending-write, scoreboard, dependency-ledger, stale-fill, Ref/Shadow Ref,
merge/wakeup, generation, or watchdog failure occurred.  Both report the
same source-domain counts: loads `6584`, stores `504`, atomics `0`, and
source-reachable `FENCE_OP` `0`.

## R4C.6: closed-stage regression

The final build/CMake test suite above passed.  Final-source VecAdd self-checks
also passed under PAPER_IO, PAPER_OO, MODERN_OO_SECTOR, and LEGACY:

- IO: lower created/issued/responded `16/16/16`, dependencies `16/16`,
  credit acquire/release `16/16`, PIB/inflight/outstanding `0`;
- OO: lower `16/16/16`, dependencies `16/16`, active refs/PIB/inflight `0`;
- sector OO: lower and wakeups `64/64/64`, line dependencies `16/16`, active
  refs/PIB/inflight `0`;
- LEGACY: `vecAdd result: PASS`, confirming no DTC-mode repair leakage.

## R4C.7: PAPER_BASE timeout disposition

The prior 240-second timeout was rerun with a 420-second diagnostic allowance.
It made continuous simulator progress: approximately 14,500 cycles at 36 s,
27,500 at 77 s, 56,000 at 158 s, 98,000 at 278 s, 130,000 at 360 s, and
152,000 at the end of the allowance.  No native deadlock/watchdog, assertion,
or crash appeared.  The run is therefore classified **SLOW_BUT_PROGRESSING**,
not `NO_PROGRESS_DEADLOCK` or a correctness failure.  Its config hash remains
`ec2a9871fc7ecbaff057f9486935792b45fe711d9569888a6d3c7f2453cd7823`; log
SHA-256 is `a79cf9ae7051205e6f1ec1705695648f8a632275b5074362f3d748681c0d53a4`.

## Disposition

R4C.0--R4C.7 are closed PASS.  No PTX fence frontend support was added and no
`membar` was mapped to `FENCE_OP`.  M1--M3 remain closed; M4 may resume at the
authorized source-reachability/fence disposition and remaining workload gates.
