# REVIEW_CLARIFICATION: preview phase versus backend detach phase

Main and independent Agent D identified a claim boundary in the initial report. The original report and original delivery manifest are preserved byte-for-byte in revision_history/initial_before_phase_claim_clarification/.

Unchanged PROVEN observations:
- Rows phase has TP CONSULTED_MISS virtual-relief preview/admission counts B=237, C=360. Columns phase has 0 in both arms.
- Rows C previews split into 63 ordinary-request and 297 RO-candidate observations.
- Whole-application actual backend detach_success is B=237, C=360, with accepted final drain/NI scope.
- Kernel cycles and every CSV number remain unchanged.

Corrected claim:
- Preview totals equal global actual backend totals. This is an aggregate closure check, not a per-event pairing or backend per-kernel counter.
- All phase-recorded successful virtual-relief previews are in Rows: PROVEN.
- All actual backend detaches are in Rows: UNKNOWN as directly measured evidence in this delivery. Source-supported localization is plausible but not upgraded without a complete proof covering every backend entry and excluding any new/restored eligibility or alternate unrecorded route between snapshot and commit.
- Columns improvement is LIKELY an indirect state/schedule effect; the current phase preview evidence does not prove direct Columns detach acceleration. Exact mechanism carrier and exact actual backend phase remain UNKNOWN.

No new raw read, model launch, collector change or CSV numerical change was performed for this clarification.
