# V4 exact6 final closeout

All three separately approved families are CLOSED_COMPLETED: approved6, consumed6, accepted6, remaining0. No additional model starts, retry or refund. Every accepted application drained hardware, passed complete declared-population checks, full-SHA genuine164 archive and two distinct complete Native restores.

| Input/mode | Complete cycles | Matched comparison |
|---|---:|---|
| Stencil S G64x8 | 4299729 | REF5242939; -943210 cycles, 17.9901% reduction |
| Stencil WV_ZERO_RO G64x8 | 4282418 | REF4768893; -486475 cycles, 10.2010% reduction |
| transpose S G64x8 | 200330 | REF200330; unchanged |
| transpose WV_ZERO_RO G64x8 | 200972 | REF200972; unchanged |
| Vector W_ONLY G32x8/1700 | 45446 | S45974; -528 cycles, 1.1485% reduction |
| Vector WV_ZERO_RO G32x8/1700 | 45425 | W45446; -21 cycles, 0.04621% reduction |

Stencil has 100 kernels, 2,193,446,000 instructions and 6,400 CTAs in each mode. At the new matched G64x8 background, WV minus S is -17,311 cycles (0.4026% reduction); at REF32x8 it was -474,046 cycles (9.0416% reduction). Report both absolute geometry improvement and the smaller same-background EP increment. Do not attribute all of the G64x8 improvement to EP.

Transpose has24 kernels/208,428,288 instructions/24,576 CTAs per mode. WV is642 cycles slower than S (0.3205%). Its exact same-mode geometry comparisons are both zero. Vector has1 kernel/56,000,000 instructions/15,625 CTAs per mode. Existing F55925 remains a combined-mode contrast, not an independent T effect.

Logical tags per slice: G32x8=256, G64x8=512, G32x16=512, G64x16=1024. This is a capacity/association comparison, not measured area/PPA/equal-area evidence. Preserve all prior G32x16/G64x16 measurements. Stencil benefits from the candidate while transpose is insensitive, so G64x8 remains a useful candidate rather than a universal optimum. Vector's small additional V gain motivates further cost/lookup/scheduling/port scrutiny before expanding mechanisms.

## Operational incidents preserved

Vector W exited naturally and was temporarily held before numeric parsing because the copied pure consumer retained an old mode_contract pin. Main's explicit consumer-only amendment rebound that one loaded-module pin to the unchanged contract already bound by Spec/NativeQ. All original outer checks and frozen numeric math were retained. Original Spec/raw/HOLD and the old V3 failures were kept; neither Vector model was rerun.

Both Stencil models exited naturally in approximately3.28/3.26 hours on November4 UTC. Their acceptance startup was blocked because authorized DTC remaining28 and V2 exact16 routes had been added to shared Native. The original guard correctly rejected an unreviewed mutation. The metadata supervisor subsequently expired without completing publication. On November5 Main independently verified that current Native is exactly those two finite authorized additions plus the byte-identical old EP Native suffix. Only the own A1 closed-result route binding was refreshed, with the old route archived. No shared Native, monitor, Core, ELF, Spec, raw, budget consumption or foreign row was modified by the closeout. The unchanged guard then passed and both original closed results completed acceptance/archive/two-restores.

See MAIN_FOREIGN_ROUTE_REVIEW.json, A1_ROUTE_BEFORE_REVIEW.json, A1_ROUTE_GUARD_REVIEW_PASS.json and ALL6_FINAL_ARCHIVE_READBACK.json here. The expired supervisor record remains available; this is a Main foreground closeout, not an automatically resumed model run.

## Remaining research outside this approved batch

A2 3MM: CPU input/mode review and private request3 graph are prepared; the new WV_REF32x8 measurement remains absent and all3 starts remain unapproved. No oldF substitution.

C: the private functional quota contract explicitly charges two row lanes plus one signed atomic count lane, READ/COMMIT cycles, merge ordering and backpressure. Production handshake integration, physical timing/PPA and a new sameSource baseline remain open. No C model was started.

No paper edits, Trace capture, extra NI models, frequency sweep or109 GPU work. Application numeric oracle/NI limitations remain as originally declared. Source KEEP and original V3 eight accepts/two failures remain unchanged.
