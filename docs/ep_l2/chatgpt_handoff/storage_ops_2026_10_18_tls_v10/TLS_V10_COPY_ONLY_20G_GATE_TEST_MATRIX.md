# TLS-V10 COPY_ONLY 20-GiB admission isolation and regression tests

This is a companion to the immutable, user-approved **scoped** amendment `TLS_V10_COPY_ONLY_20G_RESOURCE_AMENDMENT_20261019.md` at commit `c3b024d4d4325c7e52d19f3c8728530f250601c6`. These tests are dry-run/synthetic only and must not touch any frozen scientific source or re-open completed Goals.

**Implementation requirement:** Opt-in policy identity tied to the exact TLS-V10 Source Goal and frozen manifest/txid, e.g. `TLS_V10_COPY_ONLY_20G_20261019`. A broad global lowered `/workspace` threshold, environment-only unbound override, or reuse of a source-unlink gate is NOT acceptable. Default remains 48GiB for every other operation, particularly source release and all scientific executors. Do not alter original central resource accounting code/registry or mask a PID/lease.

Minimum finite dry-run matrix to publish in a SHA-bound receipt:

1. TLS-V10 + source COPY_ONLY + correct namespace/dev + 20GiB-plus expected local overlay writes + all other gates satisfied => policy eligible (NOT actual READY).
2. Same source at 19,253,473,280B => RESOURCE_HOLD; exactly 20GiB with 32MiB planned overlay writes => HOLD unless no actual overlay allocation is needed and projected remaining available remains >=20GiB.
3. Identical TLS selector with wrong operation (simulation/build/release/reverse restore) => original 48GiB applies; 20GiB does NOT pass.
4. Missing exact amendment SHA/policy ID, mismatched group txid/selector/target root, non-original174 namespace, stale source snapshot or `f_bfree` used in place of `f_bavail` => HOLD.
5. Share <40GiB, MemAvailable <64GiB, active conflict in registered/physical PID/cwd/FD or scheduled reader, insufficient lease, >256MiB staged bridge or >30MiB/s plan => HOLD.
6. P9 poller/matrix-v2/staging, mixed TLS-C2P, shared traces, modified/uncommitted code and symlink/hardlink ambiguous roots => KEEP/HOLD regardless of 20GiB.
7. A sole correct first range `TLS_V10_P9_PUBLIC_B0001` request exists without source-signed valid READY => target remains WAITING/HOLD; no scientific payload copied and no new target reservation.
8. Source future exact release list and any previous 903 `.vvp` scratch release remain outside this policy; no unlink is authorized by these tests.

Source owner should publish `TLS_V10_COPY_ONLY_20G_POLICY_TEST_RECEIPT.json`, with test cases, actual policy caller, original unmodified default gate, per-case expected/observed decision and real-source current read-only snapshot. Target independently checks original policy text SHA and exact source-signed test receipt identity before accepting a source READY, but does not run source gate or loosen a target threshold by itself.

All scientific assets and frozen group manifests stay immutable throughout. Tests passing is necessary, never sufficient, for copying a scientific payload. Actual current source resource+reader admission must still occur before each staging range.
