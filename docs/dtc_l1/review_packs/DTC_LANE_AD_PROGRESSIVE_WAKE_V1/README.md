# DTC Lane AD progressive waiter wake V1

**PASS — CPU component qualification, with explicit scope limits.** Final CTest9/9. No full simulator, native benchmark or performance run. Payload/ISA load-value correctness remains UNPROVEN.

- Host: huangrulin-174, uid0. Fixed X2 base Core `e32afdcf44be3374ff36d22568ed01a075459b6f`; Framework review parent `631eb6418f6e7f1f548afd33351cbc0d98d27145`.
- Fixed Core HEAD: `2af61a3efae8ab7994a81c81feff8e9e717dab53` on `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-core-174-v1`.
- Framework branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-174-v1`. Final publication receipt/read-back identifies its HEAD.
- `-gpgpu_dtc_l1_progressive_wakeup` defaults0; ON requires PAPER_OO + finiteV1. Other ON configurations fail closed. K1 stays independently opt-in at the original LDST source request.

AD separates complete128B data availability at the unchanged metadata edge from broadcast completion. A consumer with all held allocations data-ready and its own pending/external deps0 can enter the original LDST admission/fence/collection/WB flow. Other consumers remain pending. Notification bandwidth stays4/cycle; Ref is retained until original successful WB-retire. K1 hides lookup while protecting old physical/generation/PIB/Ref/return ownership.

Read [WAKE_STATE_MACHINE.md](WAKE_STATE_MACHINE.md), [SOURCE_DIFF.md](SOURCE_DIFF.md), [TEST_MATRIX.md](TEST_MATRIX.md), [METRIC_SCHEMA.md](METRIC_SCHEMA.md), [LATEST_REPORT.md](LATEST_REPORT.md), and [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md). `FINAL_CPU_QUALIFICATION.json` contains current artifact identity, test outputs/metrics and log hashes. `SOURCE_SHA256.tsv` covers changed Core files; `SHA256SUMS` covers packaged evidence. `AG_HANDOFF.md` is the user-selected notification channel; no AG worktree/raw was written.

The user explicitly approved one additional CPU test build after the original2 attempts. This build compiled the2 corrected test sources and refreshed the library build-string dependency. It made no production mechanism change. An inherited one-channel/IPOLY fixture mismatch was then fixed in CMake's generated CPU-only input; configuration and tests were rerun without another object build. Final C++ sources are identical to built commit `731be8548ad0fcc167ebfc49d5f1867f22034b4c`; final Core differs only in CMake test-input generation. The library truthfully embeds731be854, rather than claiming a fresh binary of the later CMake-only HEAD.

All required directed cases are represented in production-header or actual LDST component tests:4/5/8/9 waiters, early/late readiness, same-cycle quota, late merge before/after notification end, invalid/duplicate sector, slot reuse/stale generation, admission/capacity gates, RF WB pressure, source K1, final-Ref reclaim and fence sidecar. The LDST fixture injects prepared metadata/PIB/root/sector state; it does not replay a complete SASS issue/coalescer/interconnect pipeline. See TEST_MATRIX for the exact distinction.

Current-library OFF differential passes: fixed-X2 header traces and15 complete normal-statistics boundaries byte-identical; omitted equals explicit0. ON export is checked at9 sparse64-SM boundaries and3 repeated/nonzero1-SM LDST boundaries. Historical failed builds/tests and earlier PARTIAL receipts remain preserved and are superseded by current FINAL_* qualification. No AA5 active-result read, trace-body rescan, or change to AA5/AC/AE/AF/AG worktrees, raw data or execution authority occurred.
