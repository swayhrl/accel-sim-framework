# R101R4 local-service path localization - 174 V1 report

Stage: `AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_V1`

Final state: `R101R4_P0_AND_P1_MATERIAL_POST_L1_DOWNSTREAM_LOCALIZED`

The source audit bound the accepted path from translation completion through
normal L1 lookup/MSHR, request ICNT, partition/L2, return ICNT and normal L1
fill/completion.  P0 kept O2's pre-L1 placement with finite scheduled/ready
capacities 1/16.  Its ROI is exactly 1,130,670 cycles, a 62.1256555832%
improvement versus B0, so the accepted O2 response does not require unbounded
queue capacity in this input.

P1 restored normal L1 lookup, reservation/merge, miss and fill behavior while
locally servicing only the lower request of a qualified L1D miss.  Its formal
ROI is 2,737,282 cycles versus B0's 2,985,319, an 8.3085593198% improvement
that passes the preregistered 5% gate.  Accepted partition-side S1 improves
only 0.7256510946%.

P1 serves 1,126,400 LDG reads and 2,342,912 writes, with formal LDGSTS local
service recorded as zero.  It observes maximum finite depths 1/16, real queue
backpressure, zero duplicate/outstanding requests and full terminal drain.

An initial P1 attempt exposed a missing L1-instance guard at the generic cache
hook.  The failed raw is retained, the hook was constrained to
`L1_GPU_CACHE`, and the rebuilt binary was fully requalified.  The complete
rerun is rc=0.  A hash-bound postprocess-only recovery removed two
non-preregistered nonzero assumptions from the summarizer without changing or
rerunning simulator raw; all 57 gates pass.

The allowed localization is that material response remains after the normal
L1 miss decision but disappears at S1's partition-side placement.  This does
not isolate one downstream component and the contrasts are not additive
runtime fractions.

Native recommendation:

`NATIVE_CHECK_WARRANTED_POST_L1_DOWNSTREAM`

No Native run, FULL5, H1, sweep or new R101 mechanism was started.

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1/`

Durable root:

`/root/share/mnt164/huangrulin/awma_r101r4_local_service_path_localization_174_v1/`
