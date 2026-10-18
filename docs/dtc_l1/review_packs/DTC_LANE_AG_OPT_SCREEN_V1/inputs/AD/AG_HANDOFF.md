# AD -> AG fixed candidate handoff

User selected the AD branch handoff file as the notification channel. No AG worktree/raw/execution authority was touched.

- Core repository: `git@github.com:swayhrl/gpgpu-sim.git`
- Core branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-core-174-v1`
- **Fixed candidate Core SHA: `731be8548ad0fcc167ebfc49d5f1867f22034b4c`**
- Base X2: `e32afdcf44be3374ff36d22568ed01a075459b6f`
- Framework review branch: `hrl/iscas2027-dtc-lane-ad-progressive-wakeup-174-v1`
- Pack: `docs/dtc_l1/review_packs/DTC_LANE_AD_PROGRESSIVE_WAKE_V1/`
- Flag: `-gpgpu_dtc_l1_progressive_wakeup`, default0; ON only finiteV1 PAPER_OO. K1 remains independent opt-in source-request invalidation.

**Status: PARTIAL / ON acceptance STOP.** The production mechanism was built at72abf3e8; this fixed candidate changes only two synthetic CPU test files thereafter. Seven existing CTests and targeted ON header fanout/lifecycle subcases pass, OFF differential passes; both new CPU processes did not fully pass. Corrections need an explicitly authorized extra CPU test build beyond the original two-attempt limit. Do not treat this handoff as authorization to enable AD in a campaign or as a PASS/performance/value result.

The separate common timing field is admitted_returns_cycle; it means fully admitted + all real whole-line responses accepted, observed at the LDST service sample. Its exported retired sum is separate from old ready-conditioned fields. See METRIC_SCHEMA before joining measurements. Fixed X2 has no measured corresponding export. No modification of AG's conditions, result population or execution rights is implied.

Supplemental build-free evidence (Core SHA unchanged): all9 unsupported ON combinations reject through the existing production OO constructor;9 actual ON normal-print boundaries pass in zero/two one-waiter frontend-API states. Original CTest7/9 and full real-LDST acceptance gap remain. These supplemental checks do not authorize a campaign or change ON acceptance STOP. See SUPPLEMENTAL_CPU_EVIDENCE.md.
