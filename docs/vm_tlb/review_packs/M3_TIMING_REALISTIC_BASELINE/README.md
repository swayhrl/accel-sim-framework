# M3 timing-realistic baseline review pack

Status: `M3 PASS — G3-4A/G3-4B/G3-5A/G3-5B closed`.

The final Core implementation is `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d` on accepted G3-3 Core
`1b18b3c5`.  It selects one 64KB or 2MB translation page size per run, adds
explicit non-zero L1/L2 lookup service timing (generic seed 10/80 cycles),
and records requester critical-path intervals without multiplying shared walk
work by merge depth.  The real-PTE, hierarchy-prefix and intermediate-only PWC
semantics remain unchanged.

## Frozen M3 entry snapshot

| Repository | M2 source anchor | Entry status |
| --- | --- | --- |
| Core/GPGPU-Sim | M2 accepted `3b93e243`; G3-1-RF `a192e5dc` | pending push at closeout |
| Framework/Accel-Sim | handoff `0ca67e7c` | pending evidence push at closeout |

G3-0 is `PASS`: the completed M2 pack, M2-D diagnosis, target-mode plan,
M3 reference materials, M3 stage specification, long-lived VM specifications,
and target-paper known/unknown boundary were reread.  The compact M1 and
G2-1..G2-4 directed regressions were rerun at the frozen Core source anchor
and all passed.  M2 disabled/ideal transparency and real functional replays
are linked from the completed M2 pack.

No M3 semantics are claimed by this entry snapshot.  The fixed-latency M2
walker remains available as the required diagnostic comparator until M3
closeout.

Entry artifacts:

- [Parameter/evidence ledger](PARAMETER_EVIDENCE_LEDGER.md)
- [M2 regression freeze](M2_REGRESSION_FREEZE.md)
- [G3-1 PTE backend/request contract](G3_1_PTE_BACKEND.md)
- [G3-1-RF namespace-fix evidence](G3_1_ADDRESS_NAMESPACE_FIX.md)
- [G3-2 blocked evidence and required semantic decision](G3_2_BLOCKED.md)
- [G3-2A address provenance diagnostic](G3_2_ADDRESS_PROVENANCE_DIAG.md)
- [G3-2B trace-width extension and G3-2 closeout](G3_2B_TRACE_WIDTH_AND_CLOSEOUT.md)
- [G3-2B validation matrix](G3_2B_VALIDATION.tsv)
- [G3-2B runtime summary](G3_2B_RUNTIME_SUMMARY.tsv)
- [Trace encoding observation (non-semantic)](TRACE_ENCODING_OBSERVATION.tsv)
- [G3-2C/G3-3 hierarchy and PWC closeout](G3_2C_G3_3_HIERARCHY_PWC_CLOSEOUT.md)
- [G3-2C/G3-3 validation matrix](G3_2C_G3_3_VALIDATION.tsv)
- [G3-2C/G3-3 runtime summary](G3_2C_G3_3_RUNTIME_SUMMARY.tsv)
- [G3-4/G3-5 final closeout](G3_4_G3_5_FINAL_CLOSEOUT.md)
- [G3-4/G3-5 directed and integrated validation](G3_4_G3_5_VALIDATION.tsv)
- [G3-5A latency-accounting contract](G3_5A_LATENCY_ACCOUNTING.md)
- [G3-5B structured sensitivity summary](G3_5B_SENSITIVITY.tsv)
- [PTE conservation report](PTE_CONSERVATION.md)

The M3 evidence boundary is generic reusable VM timing infrastructure.  It is
not a claim of exact Segmentation-paper PTW, PWC, sub-entry, or commercial-GPU
implementation fidelity.
