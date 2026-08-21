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
| Snapshot response latency | 2 cycles | 2 cycles |
| logical Snapshot capacity | 5,120 x 64 b = 40 KiB | same |
| candidate ordering | cluster distance, then SID | same |
| remote-probe timeout | 32 cycles | 32 cycles |

`c2p_snapshot_matrix.v` uses the simulator's reverse-low-10-bit tag-mask
mapping and the same bit-exact folded hash function/salts.  An update only
sets Snapshot bits.  Thus stale metadata may add an exact probe but can never
return data without that probe; the peer response is authoritative.

## Interfaces and ownership

`c2p_cache_rtl.v` owns only metadata and request-control state.  The original
request payload stays in the L1/L2 integration layer; the top carries the
stable line tag and requester/target SID.  Its peer-probe and lower-memory
interfaces are ordinary valid/ready channels, with one in-order probe
outstanding per instantiated query lane.  There is no valid-to-ready
combinational cycle across the module boundary.

The current top intentionally contains **one query lane** and an eight-entry
admission FIFO.  It is a functional, synthesizable baseline for the C2P
mechanism, not yet the simulator's 128-engine / 256-transaction throughput
configuration.  Multi-lane issue, target-L1 FIFO ownership, continuous
Snapshot rebuild traffic, and the physical macro adapter are separate
scaling work; they must not be silently claimed by the single-lane PPA result.

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
SRAM.  Its default functional branch has four independent logical arrays so
directed RTL tests exercise real candidate filtering.  With
`USE_SRAM_MACRO=1`, the same matrix protocol instantiates four
`c2p_snapshot_sram_1r1w` wrappers instead.  The technology integration owns
that wrapper and supplies its Verilog/Liberty/LEF/GDS views.  The matrix clears
one row per cycle after reset, avoiding a giant resettable-flop implementation.

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

It checks candidate insertion, nearest-first probe ordering, a probe miss
followed by another candidate, peer-hit completion, true no-candidate
fallback, exhausted-candidate fallback, and requester self-exclusion.
