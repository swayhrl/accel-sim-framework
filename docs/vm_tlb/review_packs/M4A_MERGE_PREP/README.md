# M4A merge-prep review pack

This is an offline, main-server-only audit of the two immutable Route-E formal
rank-0 trace archives. It prepares evidence for later Track-A integration but
does not merge Track A, modify Core/VM semantics, recapture, access GPUs, add
Segmentation, create synthetic KV, or make a permanent NCCL policy decision.

The pack records four corrections and their provenance:

1. archive admission/integrity;
2. semantic classification from embedded trace headers rather than filenames;
3. full active-lane address decoding and conservative Weight/KV runtime-range
   coverage; and
4. bounded frozen-parser compatibility over COMPUTE and NCCL samples.

Read `ADDRESS_COVERAGE.md` and `INTEGRATION_MANIFEST.md` as the controlled handoff. The capture executable
SHA is `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`; later audit commits are not
capture executables.
