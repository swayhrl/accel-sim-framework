# B full-system V2 integration request

Use Core d1c570369da8295b01cc02cf157ed816a158d5ad additions, with
`docs/ep_l2/ms_victim/full_system_v2_r1/A645_LAST_UNPIN.patch` against exact
A6452b74d92c2cf72f80e5f5e102941d6cf9adf7a. Do not reapply old whole adapters.
The three metadata/bank/fixed modules match A645; apply only the consumer delta.

Review the complete request in review pack MS20261019_B_FULL_SYSTEM_V2_r1 /
REQUEST_TO_A_C_E.json. A owns common source/CMake/frontend/resource changes;
C owns the whole synthetic epoch and RO/common retry interaction review;
E owns independent native qualification and application budget. One combined
fixture/input is supplied with expected-only counters and no native PASS.

Keep fixed+dirty guard until the retained-WB budget-class accounting gap is
closed on A's combined preimage; clean64 is a stage, not the final fixed control.
No free map/pool/port/response buffer, no new trace and no oracle scope weakening.
