# Next architecture and minimum validation plan

Status: HYPOTHESIS/NOT_QUALIFIED design only. New formal budget0 and new starts0. No patch, collector, simulator build, CPU fixture or future admission is performed. Existing Stencil, Source and automatic publication remain untouched.

## Preferred conditional direction

Source78 already tracks event-age: install/promotion, successful response_commit (directory.h:253-257) and WB completion update it. It is not pure last-use LRU. preview_install (directory.h:164-170) prefers reclaimable CLEAN over WB_COMPLETE on dirty insertion, then compares age within the selected class; clean insertion already compares ages across classes. A second path tvd_reclaim_one (tvd-cache.inc:39-57) also uses CLEAN-first order for Payload/fixed-retention/landing pressure.

Freeze the first candidate as DIRECTORY-DIRTY-INSTALL ONLY. On a full directory, compare existing event-age across legal CLEAN/WB_COMPLETE entries, rather than an unconditional CLEAN-first preference. Leave EMPTY selection, clean incoming installs, mandatory rules and the second Payload/landing reclaim path unchanged. This is not a claim of unified global reclaim optimization. A later two-path policy would be a separate design/control, not silently added to this switch.

Use one default-OFF configuration switch in an independent newSource/ELF, preserving the legacy rule. No new served bit, free CAM probe, capacity, bank port or queue is proposed. Existing age can supply the candidate key, but selection/arbitration/timing costs still need a concrete hardware implementation argument. PPA remains UNKNOWN. No accepted Source is automatically modified.

The motivating CPU counterexample is a full directory containing a recently served eligible CLEAN and an older eligible WB_COMPLETE: legacy dirty-insert chooses CLEAN due to class priority, candidate can retain it. This sequence is a correctness/choice test, not proof it occurs frequently or speeds a real input. Include EMPTY, unchanged clean-install, recently serviced WB_COMPLETE, readers/pins, mandatory WB_STAGED/INFLIGHT, stale revision/generation and response-backpressure negatives. The unchanged second path needs a noninterference check; if later included, add explicit bank-color/payload-valid/fixed-quota tests and redefine the scope.

Protect mandatory/in-flight WB, WAD ownership, readers/pins, pending sectors/returns, directory and Payload generation. Existing extra-retention area includes WB_INFLIGHT, so it cannot be treated as all optional/reclaimable. Repeated preview must remain pure and agree with actual selection, including caller landing/bank reservations. Do not rename existing recency or head tokens as new mechanisms. More general service-history bits and negative filters are deferred until their incremental information/cost is demonstrated.
## Use Stencil to choose, without waiting in this research

Use only naturally accepted/archive-complete W/WV. W near S with WV recovering full-F gain supports V-package priority. W recovering most gain supports W focus. W/WV both near S with F faster points to remaining RO/M/background interactions, not M or T alone. Report exact deltas; do not select an equivalence threshold after seeing results. Full F is context and must pass Main's exact eligibility before subtraction.

If a legitimate negative-control decomposition remains necessary, Scan W_ONLY/WV would be exactly2 separately authorized Source78 points. It is not created or started here and cannot consume old allowances. It distinguishes harmful optional retention from W pressure redistribution. Do not pursue C1 merely to complete a mechanism roadmap if Stencil instead favors another lever.

## Minimum engineering checks, not executed

- Served/unserved clean/completed-dirty optional entries, mandatory/inflight exclusions, reader/pin and generation protection.
- Full directory, bank-color landing exhaustion, same-address WB, pending sectors, late response and complete resource release.
- Repeated pure preview and exact agreement with actual reclaim/capacity path; no double charging or hidden free metadata operation.
- Response/ICNT/lower backpressure and adversarial arrivals; bounded mandatory progress, no starvation, data mismatch, double response or leak.
- One declared bank/query/metadata hardware budget; finite selection/updates with explicit timing and PPA UNKNOWN.
- Full Source5/wholeTU/version-header/ELF/actual-option identity and legal modes; no automatic mixing host-writeV3, MSHR64, Source92 or P1 repair.

## Minimum later scientific request

After correctness/cost qualification and a decision-changing Stencil/negative-control observation, freeze one policy and two exact qualified inputs selected before runs: a genuine positive and negative control. Same-newELF policyOFF/ON per input gives4 primary model starts. This is a future proposed design, not registered allowance. Old Source78 cycles cannot substitute as the newELF reference. Keep geometry, physical Payload, bank/queue/DRAM service, clocks, input and background mode fixed; isolate the policy and declared costs. Retain positive/negative/zero outcomes and avoid per-program best-case tuning.

If passive instrumentation is necessary, enumerate its actual mode/policy/input OFF/ON NI and additional starts separately before authorization. No free NI, unbounded collection or inherited S coverage for WV/F. A small served-before-reclaim/query-outcome collector should mark terminal entries censored, default OFF and add no new production probe/service. No NI point count is silently assigned here. A single frozen configuration then needs genuinely held-out workload validation; these selected examples are not that validation.

For T, the unresolved minimum is per-phase paidquery costs, a bounded triggerUID/denial-gate/oldgeneration/completion link and optional Rows-end census at existing event sites. That needs a separately qualified Source/ELF and actual mode-specific NI before use, not a rerun of current science. No protection relaxation, Tag shrinking or further latency inflation is proposed.
