# C15 lane A bootstrap evidence lineage

`planning_sha` and initial A `HEAD` are both
`9a755b14b01c5a77a6fc98c2547616e1c490e806`.  This checkout is the
non-detached `hrl/vm-c15-static-v0` worktree at
`/workspace/worktrees/accel-sim-vm-c15-static`.

The only immediately usable historical input is the frozen C12 source at
`a268aba0d01310294074ded5bb8017e2092394c0`.  The inventory records SHA-256
of the exact Git-object contents for its provenance matrix, raw-log index, and
metadata schema.  No C12 raw log, trace, simulator, or Core source was run or
modified.

An explicitly bounded local-cache scan found no authorized Hugging Face model
cache.  Consequently this checkpoint contains no inferred model architecture,
no weight byte count, and no native/dynamic claim.  Later public metadata
queries must resolve an immutable revision and preserve the returned
config/index/header evidence before producing a model registry row.

At bootstrap the filesystem had 64,053,469,184 available bytes, below the
64-GiB C15 reserve.  Lane A therefore writes only small review tables and will
not create large cache, weight, trace, or simulator outputs.
