# M2 IO response-recovery evidence (in progress)

Status: `R2.0-R2.5 IMPLEMENTED; M2 NOT YET ACCEPTED`

Core recovery checkpoint:

`3be79d4d41f381ab07895b3a67da63224bdea62f`

## R2.0 identity rule

The DTC-owned whole-line request is recorded using its root
`mem_fetch::get_request_uid()`.  Current sector-L2 handling returns 32B child
objects to the shader; each child retains `get_original_mf()`, whose immutable
UID is the root request UID.  Response dispatch therefore uses:

1. returned request UID, if it is the root; otherwise
2. returned `original_mf` request UID.

It never consults the current logical Tag or conventional L1D
`m_extra_mf_fields`.

Bounded VecAdd trace, configuration, and logs are retained under
`/tmp/dtc-l1-r20/` in the active workspace.  Example source/runtime pairing:

```text
IO_LOWER_CREATED request_uid=73 inst_uid=121 addr=0xc0000480
RESPONSE_FIFO    request_uid=75 original_uid=73 addr=0xc0000480
```

The full 128B request is complete only after the four unique 32B child replies
cover its line; this is also when its lower credit and root object are released.

## Recovered path

- `PAPER_IO` load traffic creates one DTC-owned 128B lower request per new
  physical allocation, through a bounded private create/issue path with one
  issue per SM per cycle.
- IO responses are consumed before the conventional L1D response/fill branch.
  The dedicated inflight record validates `{physical_id,generation}` through
  `io_frontend::complete`; the observed conventional-routing counter is zero.
- The IO PIB retains a `warp_inst_t` payload and already-coalesced unique 128B
  references.  Only its FIFO head uses the regular operand-collector writeback
  resource; it retires at width one.
- Pending-write cardinality in this mode uses the same unique 128B references.
- Allocation blocking records only the currently unresolved line.  A retry
  that becomes a Valid/Pending hit clears that condition; it cannot become a
  historical sticky retirement dependency.

## Current validation

- Core release build: PASS.
- `dtc_l1_m1_common_test`: PASS, including multi-sector grouping, pending
  merge, transient block retry, valid hit, and allocation-width regressions.
- Real `PAPER_IO` VecAdd smoke: PASS (`vecAdd result: PASS`).  The final
  counters were: `io_lower_created=16`, `issued=16`, `responses=16`,
  `inflight_current=0`, `identity_mismatch=0`,
  `responses_routed_conventional=0`, `pib_occupancy=0`,
  `retire_count=16`, dependencies `16/16`, and lower credits `16/16`.

## Remaining HARD work

M2 remains incomplete.  The directed I06-I15 matrix, explicit high-MLP
no-traditional-MSHR proof, complete counter/parser acceptance, and M2 review
pack are still required.  M3/M4/M5 remain forbidden.
