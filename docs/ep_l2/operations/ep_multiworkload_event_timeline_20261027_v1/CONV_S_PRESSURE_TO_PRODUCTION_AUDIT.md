# Conv S: real Tag pressure before the actual access probe

**PROVEN: Conv S experiences real Tag allocation pressure. The accepted point's production_TagFAIL=0 is a narrower post-admission initial-ft_access-probe count; it must not be used to claim no real Tag pressure.** The hook is implemented for S/FT1, so this is a population/gating distinction, not a missing S hook. No accepted field, source, raw or qualification has been changed by this audit.

Actual producer Core78f4b59e865b136eede74df74c44c210f5b4ca04; Conv cohort EP_MULTI_CONV_S_ET1_20261027_V1, UUID132559ec-249d-4bb8-b867-92b23050ed3d;331234cycles/2kernels. Raw SHA ddf5fd9d0588c6c6a9a0635194135c5ee26d84fa24f24d78602ecbab32b8aa9c. The audit streams the real raw and cross-checks final Cmetrics LIFE arrays; it does not multiply marginal statistics.

## Exact same-head funnel

| Population/observation | Actual terminal count | Interpretation |
|---|---:|---|
|R4 raw_reservation_fail|42717|status-only native Tag-array probe at an observed frontend head|
|pressure_T_disabled|42717|same rawFAIL branch, formal S has no T/RO runtime|
|pressure_prod_probe_reached|42717|same head also reaches the real controller's **preview** Tag probe|
|pressure_relief_not_consulted|42717|same head, preview does not consult RO relief|
|pressure_frontend_denied / admitted|42717 /0|all those rawFAIL observations are denied before access()|
|ft_access_attempts / commit_raw_probe_reached|11477953 /11477953|a separate admitted-to-access population|
|raw_tag_fail_commit / denied_tag|0 /0|initial actual ft_access probe never fails in that admitted population|
|commit_accepted / commit_denied|5239872 /6238081|actual access returns, not the42717preview-stalled heads|

These pressure counters are incremented inside the same o.raw==RESERVATION_FAIL frontend callback, after the same request/cycle dedup, not independently sampled marginal counts. pressure_prod_probe_reached is particularly easy to misread: o.production_reached is set inside preview_access, not actual ft_access. Actual commit_raw_probe_reached is a different counter.

## Production and observation code evidence

All references below are relative to core/src/gpgpu-sim at the exact producer commit.

| File/function/line | Direct source evidence |
|---|---|
|gpu-cache.cc:365-452 tag_array::probe|matching requested sectors first return HIT/HIT_RESERVED/SECTOR_MISS; otherwise everyway is tested. No unreserved way leaves all_reserved=true, so450-452 returns RESERVATION_FAIL. Dirty-ratio preference has a dirty fallback436-446, not a fake availability failure.|
|gpu-cache.cc:3047-3053 detach_diag_snapshot|passive status-only raw probe of the actual target set; no held-request telemetry update.|
|gpu-cache.cc:2796-2823 preview_access|no m_ro in S, so common exact native preview runs. Its actual Tag probe is2817-2818;2820 marks o.production_reached;2821-2823 returns immediately on all-reserved failure.|
|l2cache.cc:1432-1443 /l2_admission_rules.h:45-59|line_available is false for the plan's RESERVATION_FAIL, creating LINE_ALLOC blocker; admission requires no blockers.|
|l2cache.cc:1474-1495|same cached snapshot/plan feeds R4 frontend and LIFE NEW/rawFAIL observation; inadmissible exact preview is a real production controller stall, even though access is deliberately not called.|
|l2cache.cc:1551-1593|only if admit does the controller call m_L2cache->access.|
|gpu-cache.h:3116 /gpu-cache.cc:2566-2576|ft_enabled means ft_mode!=0; both S/FT1 and F/FT2 dispatch to the same ft_access. m_ro only guards RO-specific actions.|
|ep-l2-ft-cache.inc:300-339|commit_scope starts for every FT access; actual initial probe327 and R4actual hook328 are outside m_ro. LIFE.PROD_TAGFAIL333 and ET actual-failure pressure334-335 are also outside m_ro. Only relieve at338 requires m_ro.|
|ep-l2-ro-runtime.inc:383-387|R4 ledger registration precedes conditional RO runtime construction, so S has a live diagnostic ledger.|
|gpu-cache.cc:3088-3146|once-per-head/cycle recording; same-head rawFAIL/T/preview-route/admission funnel3130-3135. The category named primary_unknown at3128 has no dedicated all-reserved Tag category; it must not erase this source-proven Tag blocker.|

Thus the42717controller-preview failures cannot reach the actual ft_access hook: exact admission has already rejected them. The zero actual count is **COVERED_BUT_NOT_REACHED_FOR_THIS_PREVIEW_FAIL_POPULATION**, not NOT_INSTRUMENTED and not absence of pressure. In F, a certified RO preview may rewrite a failed raw probe to MISS after a detachable-victim check (ep-l2-ro-runtime.inc:273-279); that separate route cannot be inferred or tested by S's T0/M0 result.

RO native-owner/directory/query/promotion gates exist in F, but Conv S has m_ro=false and no TVD. The actual42717pressure_prod_probe_reached plus zero pressure_prod_probe_not_reached excludes an RO/early-preview gate explanation for these specific observations. The common preview's WAD read gate occurs before its Tag probe (gpu-cache.cc:2808-2814); its early route is separate. The proven blocker here is line availability after the real Tag-array preview failure.

## Independent actual joint: NEW demand at R8

LIFE's frontend callback264-284 receives the same target-set snapshot and cached occupancy. NEW_HEAD counts repeated rawMISS/rawFAIL head observations; NEW_UNIQUE deduplicates the first observed NEW exposure for a FIFO head UID. The arrays are actual occupancy-at-arrival joints, not products of occupancy and arrival marginals.

- NEW first-unique atR8:289. This is not a complete count of distinct requests that ever later encountered pressure; a request first seen atR7 can subsequently retry atR8.
- NEW headcycle atR8:42717, equal to LIFE RAW_FAIL_HEAD and R4 raw_reservation_fail.
- R5 heads_raw_reserved has the single rawFAIL row[raw_status3,R8,42717], a direct same-head/same-target-set joint. R5 covers11937084heads with no skipped/unknown R4 probes; all are RO N/A in formal S.
- Sum of physical-set tick-end area[8]:202478set-L2ticks, not global elapsed cycles. Both eventpeak and tickpeak reach8.
-204physicalsets have NEW head observations atR8. Exact per-set rows are in CONV_S_R8_PER_SET.csv. Full terminal LIFE has64META/END and2048SET/INCARNATION rows, all closed/invalid0; Cmetrics arrays match the raw reductions exactly.

SUMMARY_STAGE does not emit per-set windows. Terminal per-set area and arrival joints remain complete; a missing WINDOW_SET is NOT_EMITTED, not zero. The static R5 source_base_core9243... field is wire provenance, not the runtime producer; actual current78f4Source5 is bound externally by the accepted point/SourceQ.

## What the denial totals and64samples cannot prove

Actual access denial reasons partition6238081: WAD3733023, WB1308586, copy720834, bank475185, pin453. These are repeated access attempts after admission, and their actual initial Tag probes all passed in this run. They cannot be added to, multiplied with, or treated as the same-request blocker explanation for the42717preview failures. Eventual UID linkage would need an explicit retained trace; current aggregate totals do not measure it.

R4sample_pressure has a single global MAX_SAMPLES64 (ep-l2-detach-diag.h:14,287,298), not64per physicalset or a random statistical sample. samples_seen42717/stored64/dropped42653. The64stored examples cover only2UIDs atCORE6903-6963; all immediate_commit_result=-1. commit_scope at304 updates that sample only when the same UID reaches ft_access in the same cycle; -1 is the untouched sentinel, not a measured RESERVATION_FAIL return or eventual request outcome. Aggregate R4/R5/LIFE counts are not truncated to64by this example cap.

## Claim boundary and decision implication

PROVEN: real native S frontend new-Tag pressure exists; admission excludes those failures from the later actual-probe count. PROVEN: the common actual-probe hooks cover S and their narrow zero is valid. PROVEN: same-target NEW/R8 joints are positive.

UNKNOWN: suitable detachable RO victims under a separately certified F configuration, full distinct-pressure-request population beyond first-NEW dedup, how many of the42717stalls lie on the end-to-end critical path, and whether detach could improve cycles. Formal S has no RO/T mechanism, so its eligibility/detach fields are N/A, not a measured absence of potential RO victims. This result establishes a real Tag-pressure workload, not a positive T performance result or permission to relax safety conditions.

The report-facing interpretation should retain both names explicitly: preview all-reserved head observations42717 and admitted initial-ft_access-probe failures0. Preserve the frozen accepted point and attach this postrun scope explanation; do not silently replace its value or classify the application as having no Tag pressure.

Audit executed only bounded offline parsing onCPU20/nice10/AS512MiB/wall120 after current readonly resource/PID-RSS admission PASS;RC0 in0.263s. No CPU model fixture, full application, native actor, source/spec/raw/point modification or registry/budget operation was performed.
