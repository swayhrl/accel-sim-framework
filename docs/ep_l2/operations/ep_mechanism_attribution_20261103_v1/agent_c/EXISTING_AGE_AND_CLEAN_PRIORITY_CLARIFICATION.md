# Existing age and CLEAN-priority clarification

Status: **PASS for bounded existing-source inspection; proposed policy remains HYPOTHESIS / NOT_QUALIFIED.** This additive review narrows the original generic service-aware-retention candidate. Original reports, manifests and accepted evidence are preserved. No Source edit, new raw read, CPU fixture, NI or model run occurred.

## Existing service sensitivity is real

Source78 `ep-l2-tvd-directory.h:253-257` updates `e.age=++m_age` only on actual `response_commit`, after real Payload bank service and successful response enqueue. The present policy is consequently already sensitive to successful service. Installation (`:206`), dirty promotion (`:319`) and WB completion (`:361`) also refresh age. Therefore existing age is event-recency, not strictly elapsed-time or last-demand-service LRU. Adding a generic served bit or recency update without first identifying an unrepresented distinction would duplicate existing functionality. It is incorrect to describe current reclamation as wholly unaware of service.

Entries remain reclaimable only for CLEAN or WB_COMPLETE with no readers (`:42-44`); WB_STAGED and WB_INFLIGHT are mandatory. Response readers, generation/incarnation, payload ownership and bank constraints cannot be discarded to improve retention outcomes.

## One precise existing preference that could be changed

`preview_install` (`directory.h:148-173`) uses an empty slot first. If none exists, it considers only `reclaimable()` entries:

- For a dirty incoming installation, **any** eligible CLEAN entry outranks WB_COMPLETE, regardless of cross-class age; minimum age breaks ties within the chosen class (`:164-170`).
- For a clean incoming installation, cross-class minimum existing age already applies. Removing a CLEAN preference there would not be a new change.

Thus a genuinely distinct minimal candidate is: for a dirty installation, choose minimum **existing age across both legal optional classes**, retaining all current eligibility and commit checks; default keeps the old preference. A recent actually served CLEAN entry and an older WB_COMPLETE entry can distinguish the old and proposed rules. The current class preference is a deliberate policy, not a demonstrated correctness bug. The change may preserve useful CLEAN data but may also discard valuable completed-WB data. Its real incidence and net application effect are UNKNOWN.

No new served bit is intrinsically required for this narrow candidate. It reuses an existing metadata field and finite comparison traversal. That supports a minimal implementation hypothesis, not proof of free comparator wiring, PPA or clock closure. Age refresh at WB completion means ?old WB_COMPLETE? must be constructed and interpreted relative to all existing age events, not its original installation time alone.

## A second selection path must be explicitly scoped

Source78 `ep-l2-tvd-cache.inc:39-57`, `tvd_reclaim_one`, separately loops states `{CLEAN, WB_COMPLETE}`. It therefore also has absolute CLEAN-first selection, then minimum age within that state. Unlike a directory-slot choice, this path additionally requires valid Payload and, when specified, matching `payload_id % 4` bank color. `ep-l2-ft-cache.inc:402-415` calls it under fixed-retention reservation or mandatory resident-landing pressure; epoch cleanup also uses it without a bank restriction.

Main must specify whether the single proposed policy switch covers:

1. **Directory-install selection only:** change dirty `preview_install` class preference, retain the existing Payload-pressure `tvd_reclaim_one` behavior. This is the smallest single-site candidate, but cannot be called a uniform optional-V reclaim policy.
2. **A consistent class-neutral rule at both existing selection sites:** reuse existing age across eligible classes in both, preserving the respective directory and bank-color constraints. This is still one policy family but has two production paths to qualify independently. The effects and triggering populations must be reported by path.

Neither option is implemented here. A single CPU case for directory replacement would not qualify the separate landing-pressure path. Conversely a bank-colored reclamation fixture alone would not prove the full-directory install/commit path. A plan cannot silently switch both while documenting only one.

## Minimal CPU design, proposed and not executed

First construct a full directory with no EMPTY slots, an older eligible WB_COMPLETE and a more recent CLEAN entry whose age was refreshed by real bank-service/response-commit, with all other entries protected or younger. Show old dirty install selects CLEAN, candidate selects the older WB_COMPLETE. Verify both plans preserve revision checks, generation, displacement handle ownership and successful commit. An EMPTY-slot case should be unchanged. Clean incoming install already chooses across classes and should be unchanged.

Add negative controls for CLEAN/WB_COMPLETE readers, mandatory WB_STAGED/WB_INFLIGHT, stale revision/ticket, response enqueue backpressure (no successful response_commit, therefore no fake service refresh), and a recently serviced WB_COMPLETE that the new rule should retain over older CLEAN. Repeated preview must not mutate age, selection state, allocation, query counts or resource usage. Complete WB/request drain must still release mandatory resources exactly once.

If Main includes `tvd_reclaim_one`, separately construct bank-colored eligible and ineligible alternatives, payload-invalid entries and pins, verify no false cross-bank landing, preserve protected-state rejection and progress after one legitimate release. Keep fixed-retention quotas, physical Payload, Tag/bank ports, response/lower credits and fairness intact. Do not execute new application points or call fixture cycles a GPU speedup.

## Recommendation

This is a more concrete **conditional first candidate** than adding a generic service bit or reimplementing the existing lookup token. It changes an actual class-order preference while reusing existing successful-service recency. The scientific claim remains modest: a code-constructible policy difference exists; workload frequency, time-critical value and speedup are UNKNOWN. Finish accepted Stencil attribution, freeze the exact one-/two-path design and costs, then qualify independent CPU correctness before Main proposes any new Source/performance budget. No new scan or Source modification is authorized by this addendum.
