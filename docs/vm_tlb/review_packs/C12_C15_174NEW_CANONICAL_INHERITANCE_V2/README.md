# C12–C15 canonical inheritance V2

Status: `C12_C15_174NEW_INHERITANCE_PASS_REPLAY_ENVIRONMENT_BLOCKED`.

This pack records Round-2 execution from coordination HEAD `4ca4ef4ab3f25319430b76f14ff69c1d69b158a4`, consuming destination inventory `0cc24b1d0d7829a95f9122937bf88dde8d403992` and old174 private-closeout authority `3c62c749e3c5251f6bb8e1383cb1886521008d8e` (the prior archaeology tree is `872423194e393fac9ca85171c77bafa87bde389e`). No GPU workload and no C16 formal-raw mutation occurred.

Canonical node164 namespaces were created. Three selected shared historical trees (M4C controls, M4B replay logs, and EP-L2/cache experiments; 1,532,057,733 bytes) were copied with source/destination file-manifest equality. The verified five-asset old174 private export was copied without moving or deleting source data; its control-plane SHA values and destination file checks are recorded.

Git remains source authority, not an archival source-tree copy. Normalized lineage tables retain `UNKNOWN` where launch/runtime links cannot be proven. A compatibility rebuild was attempted from Framework `d64408a...` and Core `hrl/vm-core-v0`, but failed because `/usr/local/cuda/bin/nvcc` is absent and the exact historical Core commit `57bb71...` is unavailable from the fetched remote. An existing non-matching binary was bounded-tested against a one-trace anchor; it timed out after producing simulator output and is not a reproduction claim.

Current C16 MREF-sharded data remains fail-closed for simulator conversion; see `SIMULATOR_INPUT_COMPATIBILITY_DECISION.md` and the future capture contract.
