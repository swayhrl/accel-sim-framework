# AD latest report

**PARTIAL — STOP accepting ON as fully CPU-qualified.** No scientific timing/value/performance conclusion follows from this candidate yet.

Core final candidate: `731be8548ad0fcc167ebfc49d5f1867f22034b4c`, parent X2 `e32afdcf44be3374ff36d22568ed01a075459b6f`; independent AD branch pushed/fetched back and clean. Framework pack branch is `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-174-v1`, parent `631eb6418f6e7f1f548afd33351cbc0d98d27145`; publication receipts identify payload commit and final fetch-back. No other lane was changed or its authority adopted.

Implemented default0 progressive waiter wake for finite PAPER_OO only. Matured service-return data availability is separate from row broadcast-done. Only the notified consumer with own/external deps cleared and all held allocations data-ready can progress through unchanged LDST admission/fence/collection/WB. Late attachments receive their own budgeted notification; consumed prefix is removed safely. Invisible old allocations keep Ref, physical and generation until original retirement/reclaim. Source K1, ordinary pending tag commit and real kernel completion remain distinct. No missing sectors are treated as readable, and no PROXY_FENCE is interpreted as data consistency.

PASS evidence:

- Build2 produced the production library and CPU tests with assertions enabled. Its embedded source is `72abf3e83c9ec5fcbf49616fba9b8377b845ac45`; final candidate differs only in two test files. Production source/CMake bytes are identical. This is deliberately not described as a fresh build of the later test-fix HEAD.
- All seven original CTests pass. New header test completed all eight ON/OFF 4/5/8/9-waiter fanout subcases, same-cycle quota/+1 checks, and late merge/slot reuse/old generation/K1/final-Ref/external-dependency lifecycle subcase.
- Supplemental, no compilation: existing production OO constructor exercised20 config combinations (9 unsupported ON reject,1 supported ON return,10 OFF guard-inert returns). Existing normal-export CPU fixture with ON exercised9 real statistics boundaries at64 SM in zero/two one-waiter API-fill states and1/8-core topologies;6 deliberately corrupted AD exports rejected. No actual cacheable LDST PIB traffic is covered by these passes. See SUPPLEMENTAL_CPU_EVIDENCE.md.
- OFF: fixed-X2 deterministic header traces byte-identical; fifteen actual normal-print boundaries byte-identical across K1 off/on and 1/8 cores per cluster; omitted progressive equals explicit0 at three boundaries. AD frame absent OFF. Source allowlist8 files, protected production bodies13 byte-identical.

PARTIAL / failed evidence:

- Build1 failed new header-test compilation because of a missing SM argument; corrected before Build2.
- CTest after Build2 is **7/9**, not9/9. New header test later aborts because its synthetic service clock was not advanced before a later-cycle victim reclaim. New real LDST fixture aborts before response-path checks because synthetic output-register slots were not fully initialized. Those fixture fixes and child-only assertion-signal handling are committed, but have not been rebuilt/executed.
- The user-authorized <=2 build attempts are exhausted. A concrete request for one extra incremental build of the two CPU fixtures is pending. No additional compilation was performed. If not authorized, the open acceptance gap remains the two corrected CPU tests, nonzero actual-LDST ON metrics, actual LDST sectors/WB/fence/common-boundary validation and exact runtime layout print. See TEST_MATRIX for reached versus merely prepared checks.

New bounded ON metrics distinguish per-allocation fanout/notification timing, own-dep0 legacy-gate observations, frontend-ready entries, fully admitted notified consumers, and late merges. A separate admitted/all-real-returns observation anchors retire timing; fixed X2 has no measured counterpart. Original ready/post-ready origins change under ON and cannot be compared as the same readiness-conditioned interval. No performance measurement or all-ISA architectural load-value proof is provided. Such claims remain **UNPROVEN / STOP**; payload oracle/hardware/support-domain authorization would be separate work.

No full simulator, canary/native/performance job, trace-body scan or AA5 active-result read. Raw artifacts are AD-owned, outside Git; small receipts, source delta and SHA manifests are committed. AG notification is exclusively the user-approved `AG_HANDOFF.md` in this AD branch.
