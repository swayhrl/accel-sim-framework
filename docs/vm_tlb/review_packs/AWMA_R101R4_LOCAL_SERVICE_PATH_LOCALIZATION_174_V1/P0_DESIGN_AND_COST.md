# P0 finite pre-L1 service

Arm: `P0_FINITE_PREL1_SERVICE`.

## Placement and preserved semantics

P0 uses the accepted O2 hook after translation and frontend observation but
before normal L1D access/request ICNT. It retains the original coalesced
transaction, LDG/LDGSTS dependency kind, store ACK tokens and the existing
LD/ST writeback client.

The selector is opt-in/default OFF:

`AWMA_R101R4_SERVICE_MODE=none|p0_finite_prel1`

Diagnostics use the separate `AWMA_R101R4_DIAGNOSTICS` selector. Older O2
and S1 selectors must be explicitly none in formal P0 execution.

## Frozen finite envelope

The only configuration is derived from accepted O2 maxima:

- scheduled capacity: 1 entry per LD/ST unit;
- ready capacity: 16 entries per LD/ST unit;
- ready eligibility: admission cycle + 1;
- no extra writeback/response client or port.

A qualified access encountering a full scheduled queue stays at the original
access-queue head and reports natural `COAL_STALL`; it never falls through to
L1/ICNT. If the ready queue is full, the scheduled entry remains resident until
space exists. No entry is dropped, cancelled or reclassified.

P0 separately records one-cycle READY eligibility and actual transition. A
ready-full wait is legal finite backpressure, not a fabricated latency
violation. Admission-to-eligibility earlier/later than one cycle is a hard
violation.

## Modeled cost and claim boundary

P0 is still an oracle for data service. It models only one scheduled entry,
sixteen ready entries and the original return arbitration; it does not model
data storage, lookup energy or a hardware implementation.

P0 answers whether O2 depended on unbounded queue storage. It cannot be used
with O2/S1 differences to calculate L1 or ICNT time.
