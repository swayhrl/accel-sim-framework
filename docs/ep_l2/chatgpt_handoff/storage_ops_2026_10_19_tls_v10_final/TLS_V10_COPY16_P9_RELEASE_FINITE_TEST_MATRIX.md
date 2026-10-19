# TLS-V10 explicit 16-GiB COPY_ONLY + exact P9_RELEASE policy negative tests

Applies ONLY to source/target Goals that have independently read the full frozen new user-confirmed `TLS_V10_COPY16_AND_P9_PUBLIC_EXACT_RELEASE_AUTHORITY.md`. Old47/47 20G tests remain immutable historical evidence. New synthetic tests are mandatory and must not unlink any scientific original.

## Policy isolation and admission

1. Exact correct TLS-V10 frozen, idle, separately qualified COPY_ONLY source group with source actual f_bavail=(16GiB + control-write bound) and Share40GiB/RAM64GiB/leases/receiver identity PASS => `POLICY_ELIGIBLE_NOT_READY` (not automatic READY).
2. Exactly16GiB available with zero overlay write => eligible only if all other gates PASS. Exactly16GiB with >=1 byte planned overlay write => HOLD. 16GiB minus one byte => HOLD.
3. Old source18.29GiB historical snapshot with current actual below16GiB => HOLD; old SOURCE resource PASS cannot be reused. With current actual above16GiB but stale Lane/reader/lease or no fresh exact source SHA => HOLD.
4. Simulation/build/unrelated file release or C2P/M2D source use of16G ID => original48G or relevant original deny applies. No globally replaced constant, no inherited auto-override from old20G ID.
5. COPY_ONLY group within original25 SHA-frozen manifests -> conditional eligible; arbitrary unmanifested file, modified source code, shared trace, mixed TLS/C2P, P9 matrix-v2/staging, symlink ambiguous source -> HOLD. Wrong source fs/namespace/dev, target real164 root, source selector SHA, canonical SHA, txid, nonce -> HOLD.
6. Share below40GiB or projected bridge staging crosses40GiB; RAM below64GiB or cgroup/lease shortage; >256MiB physical staging; >30MiB/s, >128MiB raw chunk; another sender or target receiver => HOLD.
7. P9 finalizer still active but bounded proven no present/scheduled future P9_PUBLIC read/write: group may separately qualify; unknown planned use or actual consumer of P9_PUBLIC => HOLD. FD absence only is insufficient.
8. A source PASS without a precise signed B0001 `COPY_READY` never permits target receive. B0001 retained original root/txid; no duplicate root creation or B0002 before canary ACK and bridge cleanup. 13 batching tests only synthetic until actual sender/receiver qualification.

## Exact conditional 141-file source release (more restrictive)

9. Release policy invoked before complete P9 full 141-file archive and independent all-file native restore => HOLD; chunk or partial path proof is insufficient.
10. Full 141 content SHA PASS but any one missing numeric metadata or any of4 directories unverified => HOLD.
11. 140/141 matches; a new file appears; any one original has changed size/hash/ctime/inode/nlink; an original target archive/restore has changed; a file is already absent => HOLD whole release rather than substitute another selector.
12. Correct all141 immutable true164 restore, fresh source file hashes/metadata, no active or future planned reference and all resource gates PASS, source-specific user-approved P9 16G ID => `RELEASE_ELIGIBLE_NOT_RELEASED`, not a deletion receipt.
13. Same release ID applied to P9 matrix-v2, P9 historical v3/v4, any of24 other frozen groups, C2P/M2D sources, Git, non-frozen output, path traversal, symlink/hardlink surprise => HOLD.
14. Copy policy ID passed to source-release executor, or release policy ID passed to COPY_ONLY input => HOLD. Source release must not be performed by174-new/target or unauthorised other namespace.
15. Crash after durable INTENT before unlink, after unlink before DONE, after DONE before reported group completion, restart/resume and repeated command -> accurate idempotent reconcile, no blind second unlink, HOLD if unresolved. Tests must verify journal write/fsync ordering with actual synthetic fixture paths and parent directory identity, not only checking JSON format.
16. Absence of qualified real-source release executable / helper lacks pre-unlink fsynced INTENT / no directory fsync evidence where supported => HOLD, not silent V9 synthetic PASS inheritance.
17. Current source f_bavail <16GiB (or will be below after projected journal writes) or Share40/RAM64/lease/readers fail mid-release => STOP with exact journal and remaining originals preserved. Never convert one interrupted release into a false all141 completion.
18. Full exact141 postrelease DONE, all expected original paths absent, nonselected files untouched, retained verified true164 archive and native restore, immediate measured source df and long-window endpoint separately => only then `P9_PUBLIC_SOURCE_RELEASED_EXACT141`; no promise of 2.7GiB actual df gain.

## Reproducibility

Publish a finite test receipt with policy implementation commit/SHA, original unmodified 48G gate, actual simulator/other unrelated denial, case-by-case expected/observed status, synthetic fixture copy/restore/releases and exact clock+file identities, including failures and retained HOLD. Source independently signs real PASS/READY only after **fresh real** preflight. Target independently verifies passed source policy receipt and exact approval source identity, but target never runs or substitutes source release permissions.
