# Changed files and scope

## Core candidate

The reproducible `O2_CORE.patch` modifies eight files relative to the accepted
R101 Core source:

- `src/abstract_hardware_model.{cc,h}`;
- new `src/gpgpu-sim/awma_r101r2_o2_service.h`;
- `src/gpgpu-sim/awma_transient_l2_policy.h`;
- `src/gpgpu-sim/gpu-cache.{cc,h}`;
- `src/gpgpu-sim/shader.{cc,h}`.

It adds only opt-in service-oracle qualification, queueing, lifecycle markers
and telemetry. L2/DRAM/VM configuration and trace bytes are unchanged.

## Framework and tools

The inherited full terminal-drain framework source is unchanged. New R101R2
tools cover deterministic input derivation, Core patch/build, regressions,
off-equivalence, formal launch, single-arm summarization, recovery-aware
cross-arm finalization and raw indexing.

## Evidence

The review pack and track-specific report are new. Large raw logs remain on
node164 and are referenced through `RAW_DATA_INDEX.tsv`.
