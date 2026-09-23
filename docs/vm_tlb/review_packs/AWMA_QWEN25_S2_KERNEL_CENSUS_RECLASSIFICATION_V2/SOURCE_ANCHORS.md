# Source anchors

- Coordination head: `b5a366fcda31ee0ba18f235288eed51b998e4589`
- Stage handoff: `docs/vm_tlb/chatgpt_handoff/awma/PARALLEL_REPRESENTATIVE_SUITE_V1.md`
- V1 authority: `hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`
- Accepted SQLite: node164 `qwen25_s2_census.sqlite`, SHA-256
  `17d9551472a4b8d090a6aa9437ff9a74d90f336ae1ab15189ed108da1041734d`
- Accepted V1 inventory: node164 `analysis/ALL_KERNEL_LAUNCHES.tsv`, SHA-256
  `7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef`
- Correlation source fields: `CUPTI_ACTIVITY_KIND_KERNEL.correlationId`,
  `CUPTI_ACTIVITY_KIND_RUNTIME.correlationId`, runtime `globalTid/start`, and
  `NVTX_EVENTS.globalTid/start/end/text`.

The correlation fields are exported by NSYS/CUPTI SQLite. The V2 decision does
not use kernel GPU interval overlap as its phase-attribution mechanism.
