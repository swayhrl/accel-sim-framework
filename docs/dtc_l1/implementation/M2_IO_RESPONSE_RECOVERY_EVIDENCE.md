# M2 IO response-recovery evidence

Status: `M2 HARD GATES COMPLETE — REVIEW PACK PENDING COMMIT`

Core implementation checkpoint:

`ec81a7771e56670588538ca2ec7945c3a4543383`

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

## Completed validation

- Core release build and `dtc_l1_m1_common_test`: PASS. The directed unit
  covers I01-I11 and the explicit 64-independent-request no-MSHR case: it
  holds 64 pending IO PIB entries (> Baseline PIB 8 and MSHR 32), while a
  second reader is a Pending hit and leaves new misses at exactly 64. It also
  covers Tag-bank serialization/four-bank service, exact LRU, delayed fill to
  original `{id,generation}`, duplicate-after-pending-eviction accounting,
  FIFO HOL, same-cycle release reuse, partial hold/no rollback, and transient
  allocation-block retry.
- Real default-80KB `PAPER_IO` VecAdd: PASS (`vecAdd result: PASS`). The final
  counters were: `io_lower_created=16`, `issued=16`, `responses=16`,
  `inflight_current=0`, `identity_mismatch=0`,
  `responses_routed_conventional=0`, `pib_occupancy=0`,
  `retire_count=16`, dependencies `16/16`, lower credits `16/16`, and
  conventional-L1D MSHR entry/merge-full `0/0`. It reports 16 IO Tag requests
  (four per bank) and no unexpected watchdog.
- I12 tiny-pool run (`logical_sets=1`, `ways=1`, `physical_lines=1`) reaches
  the native simulator deadlock detector without a recovery special case. Its
  compact DTC dump reports `pib=1`, `free_phys=0`, `allocated_phys=1`, and one
  partial entry; this run is classified `EXPECTED_RESOURCE_DEADLOCK`.
- R2.1/I14 pressure smoke with `-gpgpu_dtc_l1_lower_outstanding_cap 2`: PASS.
  It completed the same VecAdd with created/issued/responded requests `16/16/16`,
  credits `16/16`, final outstanding `0`, and `lower_cap_full_events=1190`.
  Thus the third and later candidates wait for credit rather than creating an
  untracked lower request.

The Framework strict parser now requires Paper IO request, PIB, dependency,
and credit closure fields and captures the IO physical/duplicate/HOL/Tag and
independent conventional-MSHR evidence. `git diff --check` and clean-tree
closeout are recorded in the M2 review pack.
