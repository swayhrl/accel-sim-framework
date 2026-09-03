# M1-M3 VM baseline closeout — PASS

This is the reusable, single-GPU timing-realistic VM baseline.  Its final Core
source is `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`; the required Framework
handoff read before this stage was `a105fae027150a0047d23a3a5e78b9110be9c84c`.

The formal generic default is 56-bit raw/coalesced SimVA, identity-like SimPA,
64KB pages, 32-entry fully-associative per-SM L1 TLB, 768-entry/16-way shared
L2 TLB, 32 translation MSHRs/PWQ entries, 16 walkers, real physical PTE
L2/DRAM traffic, FINITE-128 intermediate-only PWC, and L1/L2 lookup service
10/80 cycles.  A 2MB page-size run and 49-bit generic-width directed proof are
also retained; zero lookup latency and fixed PTW are diagnostics only.

See [source/path anchors](SOURCE_ANCHORS.md), [validation](VALIDATION_SUMMARY.md),
[invariants](INVARIANT_REPORT.md), [parameter boundary](PARAMETER_EVIDENCE.md),
and [limitations](OPEN_ISSUES.md).  Stop here: M4B, Segmentation, L2-TLB
sub-entry/coalescing, synthetic KV, faults/migration/UVM/MCM and multi-ASID
work require a new handoff.
