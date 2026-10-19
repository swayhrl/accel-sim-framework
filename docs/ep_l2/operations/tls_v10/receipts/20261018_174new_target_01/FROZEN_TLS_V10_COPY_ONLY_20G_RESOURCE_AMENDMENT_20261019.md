# TLS-V10: scoped COPY_ONLY resource amendment (2026-10-19)

## Decision and precedence

The user explicitly chose **Plan B** (separate, low-footprint read-only TLS archive/restore from source-file release). This amendment is an **additive, narrow exception** to the frozen TLS-V10 coordination contract at `cb955076bde74fcab6c29f7f524c649c57e79015`. It does not edit the frozen master/old174/174-new Goals and does not reset any active Goal, source freeze, txid, selector, window, V9, Lane5, or shared scientific quota.

**For source-side TLS V10 COPY_ONLY staging/streaming to the existing bounded Share bridge, and the associated target genuine164 transfer/independent restoration only**, the original-174 `/workspace` free-space admission threshold is:

- **>= 20 GiB = 21,474,836,480 bytes**, measured on the *actual old174 source filesystem* as `f_bavail * f_frsize`, never `f_bfree`.
- This 20-GiB threshold **replaces only the 48-GiB source-workspace test within the scoped copy-only transaction**. Preserve other source identity, activity, provenance, and operational gates.
- **Do not apply this exception** to simulation, compilation, test/research data generation, scientific result storage, V9, other projects, unrelated cleanup, reverse-restore to old174, or source unlink/deletion. Their original admission/permission rules remain in force. Source deletion requires a separately authorized exact selector and a separate concrete release-safety contract; successful copy is not permission to delete.

Hard unchanged limits: old174 Share available >= 40 GiB (42,949,672,960 bytes), `MemAvailable` >= 64 GiB (68,719,476,736 bytes) together with actual reservations/cgroup headroom, central leases and task activity, one source sender/one target receiver, <= 256 MiB physical simultaneous bridge staging, <= 30 MiB/s transfer, exclusive real164 destinations, readback and full-content independent restoration. Prevent any local `/workspace` bulk scratch/copy/compression/build. Minimal control/receipt writes may be performed only with explicit per-batch upper bound (normally <=32MiB total overlay writes) and refreshed source available-space projection; stage payload on Share and true164, not source overlay. Do not move the original source path.

A fresh exact source resource and activity check is mandatory immediately before each `COPY_READY` and again before each subsequent staged range; abort/HOLD on threshold crossing, changed stat/SHA/transaction, active data, Share/RAM shortfall or new readers. Do not infer PASS from an old Lane5 terminal registry; refresh PID/start_ticks/boot_id, FD/cwd/argv, registry timestamp and known/scheduled P9/C2P readers. A namespace/mount mismatch is HOLD.

**Current measured caveat:** old174's user-reported 2026-10-19 04:53:58 UTC `/workspace` available = **19,253,473,280 B (~17.93 GiB)**, below the new hard floor by **2,221,363,200 B (~2.07 GiB)**; `/root/share` available = 44,297,179,136 B. At that snapshot **COPY_ONLY remains RESOURCE_HOLD** and **no READY or new transfer is authorized**. No automatic fallback to 16 GiB, `f_bfree`, target overlay space, or an ext4 reserved-block assumption. A smaller floor, if desired, needs a distinct explicit user approval and a new bounded contract.

## Immutable preserved work

- old174 source branch `swayhrl/gpu-l2-cache-verilog:hrl/ops-174-tls-v10-source-exec-v1` last independently fetched HEAD `58fe6bf115caf15b3d43a89ea30738bfc997a1d6`; new 04:53:58 UTC audit described by user may not yet be published there. Require exact remote SHA/review receipt before treating it as GitHub-verified.
- 25 frozen, nonoverlapping TLS exclusive cold groups; 2,328 regular files; 9,206,239,232 B allocated in original frozen group records. Group/file SHA, sidecar metadata, selector and source history remain immutable. No rehash of all 2,328 merely because the floor changed. Per-range current identity+hash is still required before staging.
- target 174-new `swayhrl/accel-sim-framework:hrl/tls-v10-174new-target-exec-v1` last fetched HEAD `314a27c948fcd0329eb492afb3c808ee8103f434`.
- Existing real164 P9_PUBLIC destination, canonical manifest and selector stay pinned. Reuse `TLS_V10_P9_PUBLIC_B0001`, txid `574747b05622a2a0f3ef1a58c11044ee724e5e585d0edd5f0fc32937eda12e6b`, selector SHA256 `315c008ee1757637b4f68172f93e58c4916cda061936dc4d0125762e6aa9ba0a`, target reserved root, and initial 144-B range. Do not create a second root, change nonce or restart V9.
- old174 original P9 finalizer PID 1789922, mixed TLS/C2P offloader PID 1920891 and other C2P scripts were still reported active. Never stop/change them or assume their future input use is absent. `matrix-v2`, staging and mixed/shared traces are KEEP/HOLD unless separately fully qualified. Code, Git trees, uncommitted scripts/configs, scientific source inputs, Lane5 and unrelated projects remain untouched.
- The separate old174 scratch release of 903 historical `.vvp` objects and 62 retained uncertain files is a closed historical action, **not** part of COPY_ONLY authority. Its user-reported read-only audit says 182 historical source paths are retrievable from Git, including 83 needing parent commits, covering 360 former VVPs; that does **not** guarantee bit-exact recreation of deleted binaries. Do not expand cleanup or silently label their rebuildability PASS. Preserve immutable journal and audit.

## Permitted continuation when all independent copy-only gates PASS

1. Source and target each read this exact amendment SHA from GitHub and publish an authority/receipt pointer to the **existing** Goals; do not mutate the frozen old contract or historic receipts. Old174 is sole source owner; 174-new sole true164 receiver/restorer.
2. Source publishes a **fresh**, source-signed `COPY_ONLY_20G_GATE_PASS` with both current bytes and predicted minimal overlay writes, Shares/RAM/lease/PID/reader evidence, original project owner and exact selector, and binds existing target B0001 request. If below20, publish an exact HOLD with no payload.
3. One stage at a time: old174 stages the pinned original range to a unique bounded Share bridge; target validates immutable READY, copies via close/reopen SHA into previously reserved genuine164, verifies chunk, independently restores to a new native path and checks digest/metadata scope. Source signs SOURCE_KEEP ACK; target cleans only that precisely acknowledged bridge range; then next range. Full project restore proof only after all bytes/paths have been verified.
4. Repeat for other frozen TLS-exclusive cold groups using their existing pinned selectors, checking independent activity/availability at each transfer. Group-specific active/HOLD exceptions remain skipped. No mass local staging; chunk larger files.
5. Publish final SOURCE_TO_164 index, per-range transactions, native restore identities, original/compressed/logical/allocated byte counts, HOLD ledger and precise future deletion proposal. Until separate exact release authorization, status is `ARCHIVED_SOURCE_KEEP`, and *source-space reclaimed by TLS-V10 is 0 bytes*.

## Review constraints

This is a resource/admission exception **only** for the no-destruction copy pipeline. It is not an empirical finding that 20 GiB is inherently safe at any write rate, nor a license to borrow ext4 reserved blocks. Any host/filesystem reserve setting changes remain unauthorized. Continue only within resource/reader checks; ordinary engineering fixes are solve-and-continue without scope expansion. Any scientific identity/authority question or inability to meet current floor is explicit HOLD rather than an automatic fallback, unproved deletion, false READY or stale receipt reuse.

Role-specific one-message instructions are in the two companion `TLS_V10_COPY_ONLY_20G_*_CONTINUATION.md` files published with this amendment.
