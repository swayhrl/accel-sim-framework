# Figure captions and layout scope

**FIG02_HISTORICAL_OPTIMISTIC_READ.** Historical OLD_D512_STATIC vectorAdd_4M:
73,873 cycles OFF versus 42,918 with the optimistic read reference; 56,000,000
instructions in both. Ratio 1.721259× applies to this single historical pair.
The reference removes real read DRAM traffic and associated queueing; write
traffic changes with interleaving. It is not B16, EP-L2 implementable speedup,
a strict mathematical upper bound, or a cross-workload average. The pair's
actual binary/source are distinct from the later Lane-4 candidate build.

**FIG03_VERIFIED_SECTOR_LOCALITY.** Historical locality among eligible demand
references. Same-line reuse includes spatial continuation within a line;
exact-sector temporal reuse requires a repeat to the same 32B sector. Eight
workloads appear in the predeclared development/validation/scan order; all
13 checkpoint rows and all numerical values are retained in the figure input
manifest. Zero temporal reuse is real for vectorAdd, not a missing input.
No TVD hit rate, lower-traffic savings or borrowing benefit is inferred.

Figures are vector PDF/SVG at a provisional 3.35-inch single-column width,
with 7.5-point main labels. This is a readability/layout choice, not a claim
that a specific venue template, page limit or deadline was verified. Rendering
was visually inspected after fixing the locality legend to sit outside the
bars. PDF/SVG text remains editable/searchable.

Current formal performance figures: none. The old r2 formal_sad/WB_PAIRS PDF/SVG
and its ratio are RETRACTED_AS_SCIENTIFIC_RESULT and are listed only in
RETRACTION_APPENDIX.md. Their original bytes remain in r2; they are not copied
into this revision's figure inventory. Neither their near-tie interpretation nor
a no-capacity-benefit conclusion is an accepted current result.
