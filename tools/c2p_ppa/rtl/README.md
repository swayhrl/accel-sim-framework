# C2P RTL contract

This directory is the hardware counterpart of
`gpgpu-sim-c2p-cache/src/gpgpu-sim/c2p-cache.{h,cc}`.  It implements the
read-side C2P mechanism only: Snapshot candidate generation, requester
removal, deterministic nearest-cluster candidate selection, exact remote-L1
probe, peer-hit completion, and lower-memory fallback.  Writes, atomics,
instruction fetches, ATA, CCD, and RING remain outside this top, exactly as
they do in the C2P simulation contract's read-side scope.

## Default geometry

| Item | RTL default | Simulator default |
| --- | ---: | ---: |
| SM columns | 64 | 64 |
| Snapshot banks | 64 | 64 |
| Bloom rows per bank | 64 | 64 |
| tag-mask rows per bank | 16 | 16 |
| rows queried per line | 4 | 4 |
| Snapshot storage response latency | 2 cycles | 2 cycles |
| hardware BF-engine latency | 2 cycles | 2 cycles |
| logical Snapshot capacity | 5,120 x 64 b = 40 KiB | same |
| candidate ordering | cluster distance, then SID | same |
| remote-probe timeout | 32 cycles | 32 cycles |

`c2p_snapshot_matrix.v` preserves the simulator's reverse-low-10-bit tag-mask
mapping. Its Bloom rows come from `c2p_bf_engine.v`, a two-cycle elastic,
hardware-oriented folded hash that accepts one request per cycle when the
storage endpoint is ready. The hash intentionally differs from the simulator's
full splitmix reference, so it changes only the Bloom false-positive
distribution—not C2P correctness: every candidate is still checked by an
exact remote-L1 probe. An update only sets Snapshot bits, so stale metadata
may add a probe but cannot return data without that probe.

## Interfaces and ownership

`c2p_cache_rtl.v` owns only metadata and request-control state.  The original
request payload stays in the L1/L2 integration layer; the top carries the
stable line tag and requester/target SID.  Its peer-probe and lower-memory
interfaces are ordinary valid/ready channels, with one in-order probe
outstanding per instantiated query lane.  There is no valid-to-ready
combinational cycle across the module boundary.

The current top intentionally contains **one query lane** and an eight-entry
admission FIFO. The Snapshot front end has independent pipelined query and
update BF engines, but this is still a functional, synthesizable baseline—not
the simulator's 128-engine / 256-transaction throughput configuration.
Multi-lane issue, a 128-way BF-engine dispatcher, 64-bank/four-copy request
arbitration, target-L1 FIFO ownership, continuous Snapshot rebuild traffic,
and the physical macro adapter are separate scaling work; they must not be
silently claimed by the single-lane PPA result.

`c2p_snapshot_banked_frontend.v` supplies a separately verifiable physical-array
interface. Its default is 128 two-cycle BF engines followed by four independent
64-bank arbiters. The arbiter exposes 256 bank-command ports (64 banks x four
copies). A four-bit sent mask at each engine records individual tag-mask/Bloom-row
grants, so one bank conflict does not hold the other three physical copies hostage
and no row can be issued twice. The paper geometry selects a static 8-by-16
priority tree; the generic implementation remains only to support small directed
tests. Each copy's replies traverse seven combinational self-routing layers with
two elastic packet cuts before `c2p_snapshot_response_joiner.v` reassembles the
four results. This avoids
a flat 64-bank-to-128-engine data crossbar; an owner ID is never reused while an
earlier response remains in flight. The static selector gives fixed low-engine
priority with bounded 16-way leaf and 8-way root depth.

The functional `c2p_cache_rtl` top remains intentionally single-lane until
its target-L1 queue machinery consumes this complete request/response port
array. No throughput claim for the 128-engine front end is made by the
single-lane directed test.

Candidate ordering is intentionally pipelined in this baseline.  A selection
walks one 8-SM cluster at a time: one clock chooses the next ordered cluster
and the next applies a small priority encoder inside it.  The walk order is
still nearest cluster first and then lowest SID.  This replaces the earlier
single-cycle 64-way divide/distance/priority cone, which is not a plausible
physical timing point.  It changes control latency by at most sixteen clocks
per candidate selection, but not the candidate set, exact-probe authority, or
lower-memory fallback semantics.

## Snapshot storage boundary

`c2p_snapshot_store.v` is the explicit boundary between the C2P matrix and
SRAM. Its default functional branch has four independent logical arrays so
directed RTL tests exercise real candidate filtering. With
`USE_SRAM_MACRO=1`, the same matrix protocol instantiates four
`c2p_snapshot_sram_1r1w` wrappers instead.  The technology integration owns
that wrapper and supplies its Verilog/Liberty/LEF/GDS views.  The matrix clears
one row per cycle after reset, avoiding a giant resettable-flop implementation.

The ASAP7 adapter is necessarily a 1RW implementation: a set-bit update is
read, captured in a dedicated register cycle, then written back ORed with its
mask. The capture is a real timing boundary; it removes a macro-Q to a
different macro-D path. It costs one extra update cycle, but Snapshot updates
are rebuild/background traffic and never alter query correctness. Query
admission is ordered behind accepted updates, so a later query cannot observe
the state before an earlier update merely because its BF engine is faster.

The final physical design maps the logical 40 KiB matrix to four physical read
replicas, as in the simulator and CACTI proxy.  That adapter requires a
concrete macro with:

- 5,120 rows x 64 data bits per replica;
- one read and one masked write port, or an explicitly scheduled equivalent;
- LEF, Liberty, GDS, power pins, timing corners, and RC/PDN rules.

No such technology-matched macro is bundled with ASAP7.  The CACTI result and
the current OpenROAD control proxy are therefore separate, transparent
estimates until that macro view is supplied.

## Verification

Run the directed test with:

```bash
C2P_IVERILOG_BIN=/path/to/iverilog tools/c2p_ppa/run_c2p_rtl_test.sh
```

It first checks `c2p_bf_engine` row-for-row against its mathematical mapping
and covers output backpressure. It also checks independent 64-bank/four-copy
arbitration, including single-copy conflicts and owner-tagged partial issue.
A separate default-geometry test checks the static 128-engine priority tree,
including cross-group fixed priority and bank-local backpressure. It then checks
the response fabric's contention handling and that the composed
multi-engine frontend joins all four responses, does not reuse an engine
early, and drains each transaction without duplication. It then checks candidate insertion,
nearest-first probe ordering, a probe miss followed by another candidate,
peer-hit completion, true no-candidate fallback, exhausted-candidate fallback,
and requester self-exclusion.
The command runs the same sequence twice: once through the reference storage
and once through a test-only synchronous 1R1W macro model, verifying that the
macro boundary preserves the two-cycle Snapshot response contract.
