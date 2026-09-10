# C12 Operator-Aware Reference Anchors

## 1. Current source state

Analysis branch base:

- Framework source checkpoint: `269c274712f4eeaee15d304033a9e6d61b5b3206`
- Source branch: `hrl/vm-m4b-speculative-v0`
- Source checkpoint status: C12 `20/22` terminal PASS
- Remaining at checkpoint 07: Prefill F1, Prefill F8-Lseg20

Do not treat this file as proof that C12 stayed at 20/22. At runtime always `git fetch` the source branch and record the newest formal C12 commit actually consumed.

## 2. Frozen C11/C12 execution identity

- Framework functional/config anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- linked binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- PA contract: `C5_MODELED_PA_HIGH_UNUSED_BIT_V1`
- PA semantics: explicit modeled non-identity driver PA; not measured NVIDIA physical address

### ROI trace identity

Prefill:

- 692 compute kernels
- compute-only trace SHA-256: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
- registration SHA-256: `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`

Decode1:

- 740 compute kernels
- compute-only trace SHA-256: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
- registration SHA-256: `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`

## 3. Semantic-kernel foundation

Primary evidence:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/SEMANTIC_KERNEL_CLASSIFICATION.md`

Known facts:

- raw Prefill list: 724 entries = 692 COMPUTE + 32 NCCL
- raw Decode1 list: 772 entries = 740 COMPUTE + 32 NCCL
- opaque trace filename is not a semantic kernel name
- semantic name must come from embedded `-kernel name = ...` trace header
- Prefill compute-only SHA = C12 Prefill trace SHA
- Decode compute-only SHA = C12 Decode trace SHA

Semantic derivatives originally lived under:

- `/workspace/m4a-merge-prep/prefill-semantic/`
- `/workspace/m4a-merge-prep/decode1-semantic/`

These paths are historical local paths, not guaranteed runtime paths. If missing, rebuild semantic manifests from immutable trace archives/lists using the existing classifier; do not invent replacements.

## 4. Runtime allocation / Weight layout foundation

Primary references:

- `docs/vm_tlb/llm/METADATA_SCHEMA.md`
- `util/llm_trace_capture/llama_tp_workload.py`

The capture sidecar contains:

- one rank-local flat `WEIGHT` allocation;
- flat allocation SimVA base + size;
- `weight_layout.tensors[]` with parameter `name`, `offset_bytes`, `size_bytes`, dtype, shape;
- runtime KV event observations where visible.

Use this information only after proving the trace global-memory address namespace can be directly compared to sidecar SimVA, or after proving the exact conversion.

## 5. C4 object/locality foundation

Reference only, not C12 performance baseline:

- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/TRACE_LOCALITY_OFFLINE.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/OBJECT_VM_STATS.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/L1D_L2_OBJECT_SUMMARY.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/CROSS_LAYER_TRANSLATION_L1D_L2.tsv`
- `util/vm_tlb/analyze_m4c_trace_locality.py`

Useful accepted workload facts from C4:

- Weight is a small fraction of dynamic trace references but dominates unique 64KiB translation pages;
- Prefill and Decode translation pressure differ qualitatively;
- `UNKNOWN` is unresolved and must stay UNKNOWN;
- C4 does not measure real hardware PA continuity.

## 6. C12 Cache foundation

Primary reference:

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/C12_CACHE_BEHAVIOR_FINDINGS.md`

Accepted F0 full-ROI observations include:

- Weight cache behavior is phase-dependent: Prefill strong locality, Decode near-streaming;
- KV reuse is much stronger in shared L2 than L1;
- Decode incoming Weight replacement frequently evicts Weight itself;
- these are behavior signals, not proof that a specific bypass/replacement policy improves performance.

The operator-aware task should test **which operators contribute these full-ROI observations**, not assume the answer.

## 7. C12 fair-arm comparisons to preserve

From `C12_C5_FULL_ROI_FAIR_PERFORMANCE_GOAL.md`:

- F0: exact-768 baseline, 66,000 bits
- F1: Sub-entry G96, 59,802 bits
- F2: exact-688, 59,125 bits
- F5: physical PWC120 + exact656, 64,745 bits
- F9: exact656, 56,375 bits
- F7: Segment N8 + exact320, 65,300 bits, Lseg 5/10/20
- F8: Segment N8 + G32, 57,734 bits, Lseg 5/10/20

C12 operator-aware analysis must not change these arm definitions or mix results from different execution identities.

## 8. Evidence hierarchy

For this window:

- direct parameter range + exact/trace-derived metric -> strongest operator evidence
- direct semantic kernel name + exact/trace-derived metric -> strong operator evidence
- sequence/model-structure inference -> heuristic only
- unresolvable -> explicitly unresolved

Formal paper-facing claims must keep these tiers separate.

## 9. Current known questions, not conclusions

The operator-aware analysis is expected to investigate, not presuppose:

- whether FFN/MLP or Attention projections dominate Weight translation footprint;
- whether Attention core kernels dominate KV L2 reuse;
- whether Segment benefit/penalty is concentrated in a few operators;
- whether strong Lseg sensitivity is broad or operator-localized;
- why large reductions in translation slow paths yield limited full-ROI speedup in some arms;
- whether F8 adds meaningful Sub-entry benefit beyond F7 for any operator.

Do not promote any of these questions to conclusions before evidence is generated.