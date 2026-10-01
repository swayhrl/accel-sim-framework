# C16 problem discovery V2: translation/TLB screen

Decision: `NO_C16_TRANSLATION_PROBLEM_QUALIFIED_YET`. This is a CPU-only screen of existing C16 address captures and primary translation papers. `TRANSLATION_TIME_HEADROOM_UNKNOWN`; no new 109 contract was generated.

Start with [the decision](FINAL_DECISION.json), [the literature timeline](GPU_TRANSLATION_LITERATURE_TIMELINE.md), [the VA proxy](C16_VIRTUAL_PAGE_PROXY.tsv) and [the screened problems](TOP_TRANSLATION_PROBLEMS.md). The 18-field [paper matrix](LITERATURE_EVIDENCE_MATRIX.tsv) gives per-paper disclosures. The independent reusable notes are at `docs/vm_tlb/literature/C16_TRANSLATION_TLB_LITERATURE_NOTES.md`.

## Result at a glance

The single captured expert down-weight shard spans 48, 88 and 64 unique 64 KB virtual pages for Q30, DeepSeek and OLMOE respectively. In those same shards, warp touches per 128 B line are 2, 2 and 1, while warp touches per 64 KB page are 86.67, 48.36 and 16.00. This is a concrete line/page distinction. It does not measure TLB service. The tensors differ in size, and each run covers only one expert and one selected static memory reference. The old Qwen2.5 AWQ shard has nonzero VA addresses that do not map to its object context; it is analyzed as `UNMAPPED_OBJECT_VA_PROXY` only.

Metric units matter: `dynamic refs` are active nonzero lane references; `warp touches` count a page or 128 B line once per warp record. `same_page_lane_fraction` is the fraction of analyzed lanes on their warp record's most common page. `lane_ref_page_transition_rate` follows the recorded lane-reference sequence within the selected static shard. Reuse distance is in that shard's warp-record units. These are address-stream statistics, not TLB probes.

The paper by Cheon et al. directly supports long-lived LLM weight versus growing KV translation competition in its modeled setting. Current C16 captures do not reproduce that page timeline or its timing. No MoE inter-expert page-set jump can be measured from the isolated shards. The checked strong neighbors include Mosaic, Avatar, LATPC, SoftWalker, cuPTW, DEPOT and weight Segmentation; wafer-scale papers are kept separate.

## Files

- `C16_VIRTUAL_PAGE_PROXY.tsv`: recorded numeric VA page metrics for one selected existing shard per capture and three page granularities.
- `PAGE_WORKING_SET_CURVES.tsv`: cumulative page sets at 25/50/75/100% of each selected shard's record stream.
- `SOURCE_SHARD_SELECTION.tsv`: deterministic maximum mapped-weight-ref selection, with explicit unmapped fallback for AWQ.
- `MOE_PAGE_BEHAVIOR.tsv`: shard coverage control and inter-expert unknowns.
- `SEGMENTABILITY_STATIC_SCREEN.tsv`: object-specific static suitability, with physical contiguity left unknown.
- `AI_TRANSLATION_SPECIALNESS.tsv`: literature-supported scenario comparison.
- `TRANSLATION_HEADROOM_STATUS.md`: oracle eligibility and timing boundary.
- `TOP_TRANSLATION_PROBLEMS.md`: final candidate guards.
- `GPU_TRANSLATION_LITERATURE_TIMELINE.md` and `LITERATURE_EVIDENCE_MATRIX.tsv`: chronological and per-paper evidence.
- `c16_translation_proxy.py`: deterministic CPU parser and synthetic record self-test.
- `verify_pack.py`: schema, numeric, SHA and deterministic rerun verifier.
- `SHA256SUMS`: pack file hashes, excluding itself.

## Provenance and validation

Terminal C16 state: `ca6c33ae0431d91aa7c6a43cbb79522402dd7580`. The branch starts at this exact commit. Raw captures are immutable under `/root/share/mnt164/huangrulin/c16_ai_workload/raw/`; exact selected paths and SHA256 are in the TSV. The `C16WARP1` record contract was checked against `c16warp1_v39_common.h` in the accepted OLMOE producer worktree (40-byte header, 280-byte warp record); the producer's serialized header was checked in `mem_trace.cu`. C16 numeric address namespace cautions follow the root `AGENTS.md` SimVA contract. The later C16 E1 trace namespace decision is a source-check for a separate traceg format, not a reason to reclassify this older AWQ object map.

Run from this repository root:

```sh
python3 docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_V2_TRANSLATION_TLB_SCREEN/verify_pack.py --rerun
```

This parses only existing files on CPU, runs a synthetic directed record test, regenerates the three proxy TSVs in a temporary directory, compares bytes and verifies `SHA256SUMS`. It does not start a GPU, profile, simulator, or mechanism run. `git diff --check` and `git status --short` are the final Git gates.

Open issues: no C16 translation timing authority, no cross-expert same-process address sequence, no C16 weight/KV page timeline, AWQ old shard object mapping mismatch, and no physical allocation/fragmentation proof. No whole-decode speedup was estimated.
