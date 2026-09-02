# M3 OO + sector implementation evidence

Status: **PASS — M4 authorized**.

Core checkpoint for the runtime evidence:
`ddf2644fb095a6f6d1a04b46a18a031c2f7de924`. The final M3 Core commit adds
the O13 CTest harness without changing simulator runtime code.

## Source-backed path

- `ldst_unit::dtc_l1_oo_memory_cycle` owns both `PAPER_OO` whole-line and
  `MODERN_OO_SECTOR` paths; only the latter iterates the original coalesced
  line's sector mask.
- `memory_sub_partition::breakdown_request_to_sector_requests` preserves a
  request already sized to 32B with exactly one sector-mask bit. The sector
  path therefore creates lower reads at `line + 32*sector`, with 32B size and
  the original line-relative mask bit.
- Root request UID plus `get_original_mf()` remain the response ownership key.
  Completion checks `{physical id,generation,sector}` before clearing one
  sector wait dependency.
- `sector_oo_frontend` retains 128B Tag-to-physical mapping and a single Ref
  per live coalesced line reference; only sector states and waiters are split.

## Deterministic validation

`dtc_l1_m1_common_test` covers O01–O12, S01–S09, and the IO-vs-OO causal HOL
pair. `dtc_l1_bad_generation_test` forks a child that injects an old physical
generation into `oo_frontend::complete`; the parent accepts only `SIGABRT`.
Release build and both CTests pass.

## Runtime validation

The existing VecAdd self-check was run with the same workload binary in modes
2, 3, and 4. All runs report `vecAdd result: PASS`; every created request was
issued and answered, PIB/inflight/active refs drain to zero, and credits close.

- `PAPER_IO`: 16 whole-line lower reads and dependencies, with no DTC-owned
  response routed to conventional L1D.
- `PAPER_OO`: 16 whole-line lower reads and dependencies; active refs drain to
  zero.
- `MODERN_OO_SECTOR`: 16 line allocations / 64 exact sector requests / 64
  fill wakeups, with 16 line-level dependencies and 64 credits closed.

Raw paths, hashes, strict-parser outputs, and gate mapping are in
`review_packs/M3_OO_SECTOR/`.
