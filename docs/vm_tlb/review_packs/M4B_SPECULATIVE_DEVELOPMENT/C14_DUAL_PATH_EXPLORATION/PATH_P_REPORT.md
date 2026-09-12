# C14 Path P — Segment-positive exploration

Status: `NO_GO_WITH_EVIDENCE`.

All rows below are `EXPLORATORY_MICRODIAGNOSTIC` and
`STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`; no cold single-kernel cycle value is
used as a full-ROI estimate.

## Result available at this checkpoint

| Selector | Cold cycles | Race admissions | Segment winners | L1 winners | fallback | Segment winners with no L2/MSHR/PTW/PTE | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| P-FFN-L0 | 435248 | 806276 | 526302 | 278974 | 1000 | 526302 / 526302 / 526302 / 526302 | PASS |
| P-FFN-L7 | 437966 | 806902 | 526573 | 279329 | 1000 | 526573 / 526573 / 526573 / 526573 | PASS |
| P-FFN-L15 | 445451 | 813680 | 529942 | 282738 | 1000 | 529942 / 529942 / 529942 / 529942 | PASS |
| P-AP-L0 | 139079 | 216159 | 132791 | 82728 | 640 | 132791 / 132791 / 132791 / 132791 | PASS |
| P-AP-L7 | 138163 | 215783 | 132553 | 82590 | 640 | 132553 / 132553 / 132553 / 132553 | PASS |
| P-AP-L15 | 140732 | 216788 | 133194 | 82954 | 640 | 133194 / 133194 / 133194 / 133194 | PASS |
| P-OTHER-TOP | 59497 | 65536 | 0 | 62712 | 2824 | 0 / 0 / 0 / 0 | PASS |
| P-EO-691 | 18699542 | 25658519 | 16420796 | 8965179 | 272544 | 16420796 / 16420796 / 16420796 / 16420796 | PASS |

The four trailing values are, in order, `l2_not_issued`,
`mshr_not_allocated`, `ptw_not_started`, and `pte_not_issued`.  For every
completed Segment winner they exactly equal the Segment winner count.  The
same winners did consume the admission-time L1 port; completed direct Weight
samples showed the L1 shadow as an ordinary miss rather than a separate late
completed request.

## Interpretation

The telemetry corroborates—not substitutes for—the source proof: the only
work raced with Segment is exact L1 lookup.  It is not an exact L2 probe, MSHR
allocation, walk, or PTE request.  Consequently, C14 finds no redundant
exact translation work on this path that a “Segment-before-L2” gate could
remove.  The limited L1 port cost has no supported cancellation boundary.

The terminal E/O row extends the same result to the selected hot
embedding/output trace: all `16420796` Segment winners avoided the downstream
exact translation backend.  Prototype decisions and the on/off timing receipt
are in `PATH_P_PROTOTYPE_AUDIT.md`.
