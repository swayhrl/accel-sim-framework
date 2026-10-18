# AD CPU test matrix

Current status: **PARTIAL / ON acceptance STOP**. No claim that all required CPU tests passed. Production implementation is compiled; fixture corrections are committed but not yet rebuilt because the user limit of <=2 build attempts has been consumed. Additional one-pass test-only build approval was requested. No third build has been run.

| Case | Header/API result | Real LDST result / limit |
|---|---|---|
| 4,5,8,9 waiters, ON/OFF | PASS: all eight subcases, first/late readiness and unchanged +1 stage | fixture prepared; overall real LDST test failed before response tests |
| Same-cycle notification quota | PASS: repeat advance does not reuse quota | prepared, not reached |
| Late merge during broadcast / after end | PASS: future notification exactly once; post-end valid hit no waiter | prepared, not reached |
| PIB slot reuse / old slot generation | PASS: early retire + slot reuse; late waiter stays pending | prepared subset; full LDST not reached |
| Old physical generation return | PASS: explicit expected child abort after generation reuse, lifecycle subcase completes | stale return through real consume path prepared, not reached |
| K1 hidden mapping, old Ref/return retained, final Ref free | PASS header lifecycle; original K1 tests also PASS | real source-request + delayed ordinary commit prepared, not reached |
| Multiple references / tag victim / partial capacity admission | PARTIAL: abort due fixture service clock3 vs access4 on retained Ref0 victim; fixed by advancing service4 before retire/access; correction unbuilt | partial admission selection check prepared, not reached |
| Duplicate / illegal / write sector response; full4x32 only | test helper assertions prepared, not reached in new header main | actual production consume-response negative/positive paths prepared; not reached due fixture register setup failure |
| WB pressure / no Ref release before grant | header Ref-at-ready checks PASS | actual RF bank reservation, pending register, scoreboard, ledger/WB paths prepared; not reached |
| PROXY_FENCE admission/same-warp barrier/sidecar retire | unchanged protected bodies PASS static; existing source tests PASS | prepared, not reached |
| ON unsupported mode / finite=0 rejection | fail-closed source guard verified static; exhaustive 9 mode/finite cases plus wrong frontend APIs prepared, not reached | supported config setup reaches GPU/LDST construction before fixture failure |
| Bounded normal ON summary/read-only repeat/common boundary | header lifecycle summary emitted | actual normal-entrypoint prepared; not reached |
| Fixed-X2 OFF behavior / statistics | PASS: two byte-identical differential header traces (OO nine-waiter+K1 and Base/IO/OO/modern coverage) | PASS: five scenarios x three normal boundaries; K1 off/on, 1 and8 cores/cluster; explicit progressive0 equals omitted; AD frame absent |
| Existing regression suite | PASS: original seven CTests | includes real ordinary-cache pending/commit and parser integration |
| Full instruction issue, actual memory hierarchy traffic, native/GPU/payload/value oracle | UNPROVEN, deliberately outside CPU metadata test scope | no full simulation, trace-body scan, performance or native run |

Failure receipts are retained, not replaced with PASS. Build1 failed compiling the new header test (missing SM argument to printer); Build2 succeeded with assertions enabled. CTest:7/9 passed, two new tests failed. The header test's earlier PASS lines are separately captured with line buffering; its process still failed. LDST fixture initially supplied uninitialized output slots because the production instruction constructor zeros only sizeof(unsigned) bytes; source decoders normally fill all slots. The fixture now explicitly zeros the complete output array. Its fork-only negative harness restores the default SIGABRT disposition in child processes so the library's crash handler cannot turn an expected assertion signal into exit1. No production assertion/decoder/scoreboard code was changed.

Raw logs remain solely under `/workspace/dtc-lane-ad-progressive-wakeup-174-v1/`. Small receipts and hashes are packaged. The accidentally attempted line-buffered LDST replay without an explicit library path failed dynamic loading and contributes no test evidence; the corrected-library replay and read-only GDB register inspection are retained for diagnosis. No GDB state edits, assertion bypasses or fabricated success were used.

Host resources are bounded; derived x86-64 libstdc++ layout delta is physical48->96 bytes (+48/slot), frontend entry56->64 (+8/PIB entry), service40->48 (+8/entry), config56->56 (new bool fits padding), plus328 bytes/frontend summary/hist and16 bytes/LDST. At default OO640/PIB128 this is33112 bytes/SM persistent added modeled-host bookkeeping (including128 LDST service timestamps), excluding container/list allocator overhead and temporary assertion maps; it adds no GPU data payload capacity. These are source/ABI-derived estimates until the final layout-print fixture is successfully rebuilt/executed.
