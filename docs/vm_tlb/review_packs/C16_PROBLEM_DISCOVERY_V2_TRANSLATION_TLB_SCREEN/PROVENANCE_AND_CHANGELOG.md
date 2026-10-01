# Provenance and closeout record

## Commit lineage

1. Bound C16 terminal state: `ca6c33ae0431d91aa7c6a43cbb79522402dd7580` (`c16-ai-workload-exploration-wave-terminal-synthesis-v1`). This branch was created at that exact commit.
2. Translation screen analysis: `0615f25c56ee43e49282c1be1d3f42dbdb782adf` (`c16-translation-tlb-problem-discovery-v2-screen`). It adds the nine required artifacts, deterministic parser/verifier, selection ledger, literature matrix and independent literature notes.
3. This closeout record and its checksum are in the subsequent branch-tip closeout commit. Inspect `git log --oneline ca6c33ae0431d91aa7c6a43cbb79522402dd7580..HEAD` for the exact tip.

## Source anchors

- C16 terminal handoff: `docs/vm_tlb/chatgpt_handoff/c16/AI_WORKLOAD_EXPLORATION_CURRENT_STATE.md` at `ca6c33ae...`.
- Accepted C16 evidence ledger: `docs/vm_tlb/review_packs/C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1/C16_ACCEPTED_EVIDENCE_LEDGER.tsv`.
- Existing `C16WARP1` record contract: `util/vm_tlb/c16/olmoe_nvbit1771_warp_regsource_v39/c16warp1_v39_common.h` and `util/vm_tlb/c16/olmoe_v40/p5_c16warp1_source/mem_trace.cu` in the OLMOE producer worktree at `52f5b86b5a50dda4d1d3413e6d456b4d7f18c565`. The on-disk header is 40 bytes; each warp record is 280 bytes.
- The exact capture directories, selected shard paths and SHA256 hashes are recorded in `SOURCE_SHARD_SELECTION.tsv` and `C16_VIRTUAL_PAGE_PROXY.tsv`. Raw files were read only and were not copied into Git.
- Independent translation literature notes: `docs/vm_tlb/literature/C16_TRANSLATION_TLB_LITERATURE_NOTES.md`, SHA256 `8a1ebb0f99c70ee7adc08c74a5c9172db1a3b6f26c8ae116097dc61fd116ce73`.
- Paper facts are linked to primary sources in `GPU_TRANSLATION_LITERATURE_TIMELINE.md` and `LITERATURE_EVIDENCE_MATRIX.tsv`. The local segmentation specification is an extraction from the user-provided paper PDF; no PDF was committed.

## Changed paths and raw-log index

Only `docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_TRANSLATION_TLB_SCREEN/` and `docs/vm_tlb/literature/C16_TRANSLATION_TLB_LITERATURE_NOTES.md` were added. The pack contains 3 page proxy TSVs, 3 screening TSVs, 1 paper matrix, 5 Markdown files, 1 JSON decision, 2 scripts and checksums. Source captures are under `/root/share/mnt164/huangrulin/c16_ai_workload/raw/`; exact run IDs and selected trace files are in `SOURCE_SHARD_SELECTION.tsv`. Each raw run contains its original `RUN_MANIFEST.json` and producer logs; no raw logs were committed.

## Validation and unresolved issues

`verify_pack.py --rerun` passed: synthetic C16WARP1 fixture, bad-size rejection, source header and static-index checks, JSON and TSV schema/count checks, page-size monotonicity, byte-identical deterministic regeneration and SHA256SUMS. `git diff --cached --check` passed before the analysis commit. Final branch status and fetch-back are reported in the terminal response.

Unresolved: no C16 translation timing or page-walk attribution; no same-process cross-expert page sequence; no C16 weight/KV competition timeline; older AWQ shard nonzero VA addresses are unmapped to its object context; physical allocation/fragmentation remains unknown. These are left as `UNKNOWN` or explicit scope limits, not converted into a speedup estimate.
