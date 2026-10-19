# ROB1 bounded preparation handoff

Status: PREPARED_NOT_TESTED; WAIT_AG4_TERMINAL_AUTHORITY.

ACK/START was published at a8a0fc962ea65f612db5a442e27157cf228dd1ae (preparation only). The coordinator's 2026-10-19T12:27:02Z observation confirms an active AG4 dispatcher, simulator descendant and execution lock. ROB1 has not checked active raw or runtime maps, executed any CPU test/script/compiler or simulator, changed production/AG4 code, acquired an execution lock, or left a background dispatcher. No new performance data or candidate selection exists in this handoff.

Completed low-pressure source review establishes the actual shared collection quota and edges, exact AE equation mapping to accepted C+ S32/24-way versus DTC S64/8-way, and AD ON-only notification/common-return metrics with OFF cells explicitly unavailable. `CONTROL_DESIGN.md`, source git-blob bindings, `AD_METRICS.tsv`, `CONTROL_REQUESTS.tsv`, a minimal proposed diagnostic collector patch, focused unexecuted CPU code and a normalized-statistics utility are published for coordinator consumption.

All control rows are **conditional requests**, not executable registrations or UUID reservations. R<=6 is enforced per selected branch: AE has service2 + up to C_ON2 + missing D_OFF2 =6; AD has service2 + missing O_OFF2 =4; F=O has service2. AE and AD branches are mutually exclusive, and missing old controls require qualification first. Calibration is not allocated here; it shares the coordinator's CAL/engineering reserve4, whose real starts (including failures) must be counted. No unused slot justifies an extra experiment.

Remaining work after release is concrete: apply/review the collector patch only in a separate c8090115 diagnostic Core; qualify actual parser/constructor/WB route and OFF/0 equivalence; if AE wins, implement and qualify the exact C+ default-OFF index change in a separate accepted6582b9d1 fork; consume only immutable terminal reuse evidence; freeze source/binary/options/inputs/F/UUIDs/timeouts and budgets. The sole coordinator owns all full-run dispatch. `CPU_RESULTS.json` distinguishes prepared code from evidence; no helper test is claimed as production integration or application-value correctness.

Git publication uses a dedicated fetched ref `refs/dtc-closure-readback/rob1` because FETCH_HEAD is shared among worktrees. The coordinator should consume this handoff at its exact final immutable commit. No hidden resumption is installed; future CPU work requires an explicit coordinator follow-up after authority release.
