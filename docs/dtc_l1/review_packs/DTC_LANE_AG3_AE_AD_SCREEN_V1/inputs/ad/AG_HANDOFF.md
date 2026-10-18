# AD -> AG fixed qualified Core handoff

The user selected the AD-branch handoff file as the notification channel. No AG worktree/raw/execution authority was touched.

- Core repository: `git@github.com:swayhrl/gpgpu-sim.git`
- Core branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-core-174-v1`
- **Fixed final Core SHA: `2af61a3efae8ab7994a81c81feff8e9e717dab53`**
- Fixed X2 base: `e32afdcf44be3374ff36d22568ed01a075459b6f`
- Framework review branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-174-v1`
- Pack: `docs/dtc_l1/review_packs/DTC_LANE_AD_PROGRESSIVE_WAKE_V1/`
- Flag: `-gpgpu_dtc_l1_progressive_wakeup`, default0; ON only finiteV1 PAPER_OO. K1 remains independently opt-in source-request invalidation.

**PASS_CPU_COMPONENT_QUALIFICATION_WITH_SCOPE_LIMITS.** The user approved the additional CPU build; final CTest9/9. Earlier candidate731be854/PARTIAL handoff is superseded. No campaign/performance/native execution is authorized by this handoff.

Current library SHA256: `17632c312e563c97aa3965ff27fa346d5e1954bc0449a6c2d1836e5ba205e302`, embedding731be854. Final2af61a3e differs from that built C++ source only in CMake's generated CPU test config (supported1-channel linear mapping); all production and test C++ files are identical. This distinction is intentional and audited.

Whole-line data and waiter broadcast completion are separate ON. Own pending/external0 plus all held allocation data-ready can enter unchanged admission/fence/collection/WB, while late/unnotified consumers remain blocked. Ref only drops at original successful retirement; K1 preserves old physical/generation/PIB/Ref/return.

Common timing boundary: admitted_returns_cycle is fully admitted + all real whole-line responses accepted, observed at the LDST service sample. Actual fixture retired-sum120; old own-ready sum112. These intervals must remain separate; neither is a cross-variant performance result. Fixed X2 has no measured corresponding common-boundary export. See METRIC_SCHEMA before joining statistics.

Coverage includes production-header4/5/8/9 waiters and actual LDST component sector/selection/collection/RF WB/ledger/K1/fence/reclaim/normal-print paths with prepared metadata. Full SASS issue/coalescing/interconnect/workload and payload/value correctness remain PARTIAL/UNPROVEN. No modification of AG's populations, conditions or execution rights is implied.
