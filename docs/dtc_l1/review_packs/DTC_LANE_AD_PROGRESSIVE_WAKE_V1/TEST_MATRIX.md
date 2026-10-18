# AD CPU test matrix — qualified

**Final CTest9/9 PASS.** Original7 regressions plus corrected progressive header and actual LDST component tests pass. The user approved one additional CPU test build beyond the original2 attempts. No fourth object build occurred. `FINAL_CPU_QUALIFICATION.json` audits actual outputs and artifact identity; all earlier failures remain in historical/raw receipts.

| Required case | Production header/API | Actual LDST component / precise limit |
|---|---|---|
|4,5,8,9 waiters | PASS, ON/OFF all8 subcases, first/late consumers and unchanged +1 | PASS9 original +1 late consumer in actual selection/collection flow; the4/5/8 variants are header cases |
|Early own-ready; late cannot advance | PASS each notification edge | PASS own-ready at11, collection12, last notifications13; late consumers unready at12 |
|Same-cycle quota reuse fails | PASS repeated advance preserves wake count | PASS repeat service11 does not notify late consumer; same-cycle second retirement rejected |
|Late merge before/after end, exactly once | PASS pending attachment/dedup during broadcast; valid hit after end creates no waiter | PASS late UID109 consumes later quota, total10 notifications for10 refs |
|Complete4x32 only, duplicate/illegal/write response | PASS response helper negatives and direct completion API discipline | PASS real consume_response requires all4 unique sectors; duplicate, sector4/out-of-line and write replies assert in expected children |
|PIB slot reuse / slot generation | PASS early retire and generation-incremented slot reused by a late waiter | Component uses production frontend; full issue/reissue scheduler not replayed |
|Old physical generation return | PASS recycled allocation rejects old generation | PASS real consume_response after4 legal sectors rejects reclaimed identity in child |
|Multiple references / partial capacity / no rollback | PASS two held allocations, early one alone insufficient, victim/physical pressure preserves Ref | PASS prepared next_reference0 exclusion while another consumer may select; full memory-cycle issue/admission loop not replayed. Existing K1 regression separately tests real frontend partial allocation/no rollback |
|WB backpressure | PASS Ref unchanged at ready | PASS real operand collector reserves competing RF bank; rejected WB retains Ref10, pending register1 and live ledger; next grant releases original resources |
|K1 source request during unfinished broadcast | PASS hidden old allocation retains generation/Refs | PASS original LDST invalidate request11 hides mapping with Ref10; ordinary pending commit14 stays distinct; old consumers finish |
|Tag victim / last Ref reclaim | PASS invisible victim retained and reclaimed on last retire | PASS final WB-retire32 frees invisible allocation; map-loss-to-free21; no live Ref |
|Fence sidecar | PASS external dependency gates own readiness | PASS production m4 admit/complete/select/retire; older same-warp PROXY_FENCE blocks younger own-ready until original completion sidecar resolves |
|Unsupported ON modes/finite | PASS9 mode/finite negatives, wrong IO/modern/paper APIs, duplicate complete | Supported parser/LDST config exercised. Existing exported production OO constructor separately rejects all9 unsupported ON combinations; full rejected LDST executable startup configurations are source-audited |
|Bounded normal ON statistics | PASS source/static33-bin and pool-bound observer; header lifecycle output | PASS three repeated nonzero1-SM frames and9 sparse64-SM normal boundaries;6 parser corruptions rejected |
|Common timing boundary | Field remains independent of readiness gate | PASS all10 retired; returns-observed-to-retire120 vs own-ready-to-complete112, explicitly separate intervals |
|OFF equivalence | PASS fixed-X2 deterministic OO9-waiter/K1 and Base/IO/OO/modern traces | PASS15 complete old public normal boundaries byte-identical; omitted equals explicit0; no AD frame OFF |
|Host resource bounds | PASS shadow Ref/pending waiter assertions, configured waiter bound | PASS sizeof physical96/entry64/config56/service48/frontend816/LDST3392; derived default persistent delta33112 bytes/SM |
|Full SASS issue/coalescer/interconnect, actual workload, payload/ISA/hardware oracle | **PARTIAL/UNPROVEN outside this CPU component scope** | No full simulator/native/performance job, trace body or real payload/value execution |

The LDST test calls actual production response acceptance, ready selection, service collection, RF operand-collector WB, ledger close/register release, frontend retirement, K1 source request/ordinary cache drain, sidecar fence and normal printer. Its CPU setup creates actual GPU/cluster/core/LDST objects but injects prepared instruction/PIB/root/sector metadata and source accounting; it does not claim complete instruction issue/lower-create/interconnect traffic coverage. Header direct complete() is trusted metadata input; real LDST sector acceptance is separately checked.

Configuration: the CPU fixture explicitly sets1 memory channel. SM7_QV100's inherited IPOLY mapping requires16/32/64 channels. CMake now writes an AD build-local config with linear indexing0; the production config is unchanged. The real mem_fetch constructor and address translator run normally. No assertion or response validity check was removed/disabled to pass.

Failure history: build1 missing printer SM argument; build2 CTest7/9 due fixture clock and incomplete synthetic output-register initialization; authorized build3 initial CTest8/9 due incompatible mapping. All failures preserved. The corrected default CTest registration now passes9/9. Configuration-only CUDA metadata/version/preprocessing probes are logged; they did not compile an object or link. Build3's requested test targets did refresh the existing build-string dependency and relink the library, with production C++ source unchanged.

No production/core assertion was deleted. Child-only SIGABRT default handling makes expected assertion signals distinguishable from the library crash reporter's exit1. No GDB state edits, assertion bypass, fabricated PASS or simulator/native benchmark was used. Raw logs remain AD-owned under `/workspace/dtc-lane-ad-progressive-wakeup-174-v1/`; small exact outputs, metrics and SHA receipts are packaged.
