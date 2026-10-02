# Compiled-path artifact attribution feasibility on node 109

Decision: `COMPILED_ATTRIBUTION_LEVEL_0_UNRESOLVED`. DQ4a: `DQ4A_COMPILED_ATTRIBUTION_UNRESOLVED`.

The 9122 Mode B correctness PASS and c483 Observer V2 identity failure are the upstream authorities. `COMPILE_CACHE_AUTHORITY.json` restores all four actual A/B cache keys/configurations from the 9122 raw runtime JSON and proves that every current cache root still matches its original content SHA. `ARTIFACT_FILE_INDEX.tsv` records 1,040 files by size and SHA. MP02 B has a pinned AOT pickle, generated Inductor output code and lowered Triton IR; MP03 B's recorded path has a readable FX graph and key factors but no point-bound generated output code.

Read `ARTIFACT_INVENTORY.tsv` for explicit PRESENT/ABSENT/UNREADABLE status. `FX_IR_PROVENANCE_MAP.tsv` records direct FX node→module/layer evidence for all 36 layers. Safe `pickletools` scans (`AOT_PICKLE_OPCODE_SCAN.json`, `AOT_NESTED_PROVENANCE_SCAN.json`) locate the embedded graph/output code without unpickling or importing torch. `OUTPUT_CODE_SOURCE_NODE_MAP.tsv` joins generated symbols to source-node comments; `KERNEL_TO_SEMANTIC_FAMILY.tsv` tests each of 96 existing Mode B runtime names against that provenance. Only the MP02 activation symbol has a direct family-only join; generic external projection kernels and MP03 B kernel instances are unresolved. `FUSION_AMBIGUITY.tsv` keeps combo/boundary work unsplit.

`LAYER_STEP_IDENTIFIABILITY.md` and `DQ4A_IDENTIFIABILITY.md` explain why static graph layer paths do not recover dynamic launch instance, layer and decode-step boundaries. `ATTRIBUTION_AUTHORITY_DECISION.json` records the conservative level. No kernel duration was used for a science claim.

The work was CPU/storage/source-only. No model load, torch/vLLM import, CUDA initialization, GPU lock, NSYS, NCU, NVBit, SASS or Accel-Sim was performed. `GPU_NONUSE_RECEIPT.json` records the task-start and final `nvidia-smi` checks. `IMPLEMENTATION_CHANGELOG.md` lists source anchors and changed files. `SHA256SUMS` covers this pack.
