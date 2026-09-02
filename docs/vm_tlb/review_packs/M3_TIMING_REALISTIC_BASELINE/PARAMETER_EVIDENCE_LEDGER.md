# M3 parameter and evidence ledger

This ledger is the M3 entry contract.  Values may be introduced only with the
label shown here; none of the generic timing choices are silently elevated to
target-paper truth.

| Item | Value/status at entry | Evidence label | Boundary |
| --- | --- | --- | --- |
| Base page | 64KB | PAPER_SPEC | target paper and frozen M2 model |
| L1 TLB | 32 entries, fully associative | PAPER_SPEC | target paper known configuration |
| L2 TLB | 768 entries, 16-way | PAPER_SPEC | target paper known configuration |
| Walkers | 16 | PAPER_SPEC | target paper known configuration |
| Trace address naming | trace address is `SimVA`; result is `SimPA` | MODELING_DECISION | simulator contract, not a claim about NVBit hardware capture stage |
| Initial data mapping | present, identity-like `SimPPN=SimVPN` | MODELING_DECISION | preserves data locality during VM bring-up |
| Translation point | coalesced transaction before real data-cache access | VERIFIED_CODE | frozen M1/M2 source contract |
| TLB lifetime | persists over ordinary kernels in a context | MODELING_DECISION | frozen project contract |
| Page-table organization | replaceable configurable radix backend | MODELING_DECISION | generic M3 substrate; not paper exact |
| Default radix level count | 4 levels if selected | REFERENCE_OTHER_PAPER / MODELING_DECISION | CLAP reference allows generic seed, never Segmentation-paper exact |
| PTE physical range | reserved deterministic non-overlapping simulated range | MODELING_DECISION | must be asserted/validated in G3-1 |
| PTE request class | explicit physical/non-recursive request | MODELING_DECISION | hard correctness invariant |
| PTE L2/DRAM timing | must use real simulator resources | VERIFIED_CODE target for M3 | no fixed-latency substitute after G3-2 |
| PWC capacity/organization | unset | UNKNOWN | choose only as labeled generic model and validate |
| L1/L2 lookup latency/ports | existing M2 configuration | MODELING_DECISION | target-paper detail is unknown |
| Segmentation L2 sub-entry | not implemented in M3 | PAPER_SPEC future boundary | M4B only |
| Page faults/migration/UVM | not implemented | MODELING_DECISION scope exclusion | resident-memory M1-M3 only |
| 2MB large pages | required generic M3 foundation | MODELING_DECISION | paper baseline remains 64KB |
| 4KB pages | optional | UNKNOWN / optional | must not delay M3 closeout |
