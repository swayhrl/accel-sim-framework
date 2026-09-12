# C16 Lane G handoff

Status: `C16_G_OFFLINE_PACKAGE_PARTIAL_READY_FOR_UPSTREAM_CLOSURE`.

C16-0.3/0.4 offline infrastructure is ready: idempotent offline bootstrap, logical env lock, unified native runner, explicit Wave-1 adapters, nsys/NCU/NVBit wrappers, receipt schema, target second-pass identity guard, shared execution-budget ledger guard, and no-GPU dry-run validation. All mock outputs are marked non-scientific and cannot enter a native catalog.

C16-0.9 is prepared but cannot close: A's fixed integration receipt hash-verifies model/input/scenario metadata, while its required GPU package and wheel closure remain unpublished pending its H-manifest dependency. No AutoDL SSH/GPU was used, no models were downloaded, and no simulator run was started. Once A publishes a fixed hash-bound package and the user provides AutoDL SSH, proceed with C16-1 inline G0/G1/G2/G3 qualification; G0/G1 success immediately releases its corresponding work while G2/G3 remain nonblocking.

Execution safety closure: every real native runner, nsys, NCU, and NVBit invocation now requires one shared AutoDL execution-budget ledger before CUDA/tool execution. The guard serializes C16 GPU operations, tracks a 24 GPU-active-hour envelope, and applies NVBit's smaller remaining/per-window 64-GiB-total, 4-GiB, 20-minute, and six-windows-per-deployment limits. Dry-runs need no ledger and remain non-scientific.

Fixed upstream consumption receipt: A final handoff commit `b458225e` passed 117 payload-hash checks. Its integration artifact checkpoint is `2a06944c359a9873ae72c89015eb5235dda2d2ee` and integration producer checkpoint is `bf2a7535d5dd96339a63567ceb13308092db0c67`; it supplies hash-bound metadata/input/scenario identities only and does not authorize GPU transfer or rental. C final handoff commit `29e669ec` passed 24 payload-hash checks; its producer implementation is `3681c506d0c4bb63ab56192474f8e8462bc7e58f`, it supplies selector protocol only, and every current NVBit row awaits G's committed native catalog. H commit `65b53574` has no C16 publish manifest and is not consumed. None of these facts authorizes native execution, profiler capture, trace collection, or a simulator run.
