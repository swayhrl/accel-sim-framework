# Changed files

## Core delta

`S1_CORE.patch` is the complete reproducible Core delta over the accepted
R101R2 runtime source. It changes only:

- `src/abstract_hardware_model.cc/.h`;
- `src/gpgpu-sim/mem_fetch.h`;
- `src/gpgpu-sim/awma_transient_l2_policy.h`;
- new `src/gpgpu-sim/awma_r101r3_s1_service.h`;
- `src/gpgpu-sim/gpu-cache.cc/.h`;
- `src/gpgpu-sim/l2cache.cc`.

The public framework commit carries the patch, tools and evidence rather than
a second embedded Core repository.

## Framework/reproducibility tools

New files under
`util/vm_tlb/awma/r101r3_bounded_service_handoff_v1/` provide:

- Stage-A offline trace/ledger analysis;
- exact Core-patch generation/reproduction;
- S1 build, directed tests and source hooks;
- OFF-equivalence and positive smoke;
- formal launch/summarization and hash-bound recovery;
- final result publication and raw/hash indexing.

## Review evidence

This review-pack directory and
`docs/vm_tlb/codex_handoff/awma/R101R3_BOUNDED_SERVICE_HANDOFF_174_V1_REPORT.md`
are new.

No accepted config, baseline source, trace payload or ChatGPT-owned handoff file
is modified.
