# M3 timing-realistic baseline review pack

Current gate: `G3-2 — real PTE L2/DRAM integration` (`BLOCKED — correctness
STOP`).  G3-2A established Case A provenance and is now stopped for ChatGPT
architecture review; no G3-3 work is authorized.

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

The M3 evidence boundary is generic reusable VM timing infrastructure.  It is
not a claim of exact Segmentation-paper PTW, PWC, sub-entry, or commercial-GPU
implementation fidelity.
