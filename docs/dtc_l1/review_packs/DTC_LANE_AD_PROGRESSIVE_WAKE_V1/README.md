# DTC Lane AD progressive waiter wake V1

**PARTIAL — ON acceptance STOP pending corrected CPU fixture validation.** Default OFF implementation and independent commits are provided; do not use this candidate as an accepted ON scientific/performance result.

- Host: huangrulin-174, uid0. Base Core fixed X2 `e32afdcf44be3374ff36d22568ed01a075459b6f`; Framework review parent `631eb6418f6e7f1f548afd33351cbc0d98d27145`.
- Core branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-core-174-v1`; fixed candidate HEAD `731be8548ad0fcc167ebfc49d5f1867f22034b4c`.
- Framework branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-174-v1`.
- Only `-gpgpu_dtc_l1_progressive_wakeup 1` plus PAPER_OO and finiteV1 enables AD. Default0. Other ON configurations abort; external-cache LDST constructor unsupported ON. No K1 setting is implicitly enabled.

AD distinguishes complete128B data at the original metadata edge from broadcast completion. A consumer with all held allocations data-ready and its own pending/external deps0 can enter original LDST admission/fence/collection/eligible/WB flow. Other consumers remain pending. Notification bandwidth remains4/cycle; Ref is retained until original successful WB-retire. K1 continues to hide lookup at the original source request and preserve old allocations/returns. No store-coherence, full ISA value-correctness or performance claim.

Read [WAKE_STATE_MACHINE.md](WAKE_STATE_MACHINE.md), [SOURCE_DIFF.md](SOURCE_DIFF.md), [TEST_MATRIX.md](TEST_MATRIX.md), [METRIC_SCHEMA.md](METRIC_SCHEMA.md), [LATEST_REPORT.md](LATEST_REPORT.md). `SOURCE_ALLOWLIST.json` and `SOURCE_SHA256.tsv` support source review. `AG_HANDOFF.md` is the user-selected notification channel; no AG worktree/raw was written.

Seven original CTests pass. The ON header test completed all4/5/8/9 fanout cases and late-merge/generation/K1/ref lifecycle subcase, then failed a synthetic clock setup. The actual LDST test failed synthetic register setup. Both fixture corrections are committed; their successful execution is unproven. Additional build-free evidence now verifies all9 unsupported ON combinations through the existing exported production OO constructor and9 actual ON normal-print boundaries through the existing CPU fixture; see SUPPLEMENTAL_CPU_EVIDENCE.md. These do not close the full LDST gap. Two build attempts are exhausted, and a separate request for one additional CPU test-only build is pending. See TEST_MATRIX for every PASS/PARTIAL and failure, not just positive subcases.

OFF CPU differential evidence passes: fixed-X2 header traces and15 complete normal-statistics boundaries are byte-identical; omitted equals explicit0. This pack contains no complete simulator/native/performance run, actual trace-body rescan, AA5 active-result read, or modifications/authority changes in AC/AE/AF/AG/AA5. Existing background tasks were not restarted, signaled or adopted.
