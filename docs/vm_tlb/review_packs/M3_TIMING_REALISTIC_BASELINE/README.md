# M3 timing-realistic baseline review pack

Current gate: `G3-1 — PTE backend / request contract` (`RUNNING`).

## Frozen M3 entry snapshot

| Repository | M2 source anchor | Entry status |
| --- | --- | --- |
| Core/GPGPU-Sim | `e7999554200760b31b4efe16d98e050370e1ea71` | clean, pushed to `research/hrl/vm-m1-m3-v0` |
| Framework/Accel-Sim | `a7020e603d6081f1f16f26b5ad1ead5ca17d7756` | clean, pushed to `origin/hrl/vm-m1-m3-v0` |

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

The M3 evidence boundary is generic reusable VM timing infrastructure.  It is
not a claim of exact Segmentation-paper PTW, PWC, sub-entry, or commercial-GPU
implementation fidelity.
