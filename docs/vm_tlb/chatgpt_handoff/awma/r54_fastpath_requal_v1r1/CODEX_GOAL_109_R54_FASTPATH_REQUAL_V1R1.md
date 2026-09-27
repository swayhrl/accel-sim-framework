# CODEX GOAL — AWMA R54 Fast-Path Requalification V1R1

## Purpose

Continue from accepted R54 V1:

- execution branch:
  `hrl/awma-r54-exact-recurrent-checkpoint-lifecycle-v1`
- accepted commit:
  `40f51deacee491d7e1b57f09db533d43d84d7ad5`
- accepted state:
  `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1`

V1 remains valid for the attempted **local package path**:
- `causal_conv1d` local build did not qualify;
- `flash-linear-attention` local package was unavailable;
- no slow-fallback timing is scientific evidence.

V1R1 tests one newly-audited official Transformers path that V1 did not exercise:

> `use_kernels=True` with the pinned Transformers Hub-kernel mappings for
> `causal_conv1d_fn`, `causal_conv1d_update`,
> `chunk_gated_delta_rule`, and
> `fused_recurrent_gated_delta_rule`.

If this official path qualifies on SM89, immediately resume the original R54 checkpoint-lifecycle contract in the same Goal.

If it does not qualify, close R54 as runtime-unavailable on the current 109 platform and STOP.

Repository:
`swayhrl/accel-sim-framework`

Coordination branch:
`hrl/awma-r54-fastpath-requal-v1r1-handoff`

Accepted base:
`40f51deacee491d7e1b57f09db533d43d84d7ad5`

Stage:
`AWMA_R54_FASTPATH_REQUALIFICATION_V1R1`

Node:
109 / RTX4080 / SM89 only.

Do not use node174 or Accel-Sim.

---

# 0. Required exact source authority

Use the exact Transformers source already accepted in R54 V1:

- commit:
  `96331a9f93b72697f160a958d2883d4b49a56739`

Read and bind:

1. `docs/source/en/model_doc/qwen3_5.md`
2. `src/transformers/integrations/hub_kernels.py`
3. `src/transformers/models/qwen3_5/modeling_qwen3_5.py`

Important exact facts from this source:

- `KERNELS_MIN_VERSION = 0.17.0`
- `KERNELS_MAX_VERSION = 0.18.0`
- the generic CUDA mappings include:
  - `causal_conv1d_fn -> kernels-community/mamba-ssm`
  - `causal_conv1d_update -> kernels-community/mamba-ssm`
  - `chunk_gated_delta_rule -> kernels-community/fla`
  - `fused_recurrent_gated_delta_rule -> kernels-community/fla`

The whole-layer `Atlas-Inference/gdn` mapping is SM121-specific and is **not** the intended SM89 path.

Do not use or claim the SM121 whole-layer kernel on RTX4080.

---

# 1. Reuse frozen V1 authority

Reuse without redownload when exact hashes match:

Model:
`Qwen/Qwen3.5-0.8B@c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb`

Expected model weight SHA256:
`04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696`

Reuse:
- V1 model files;
- V1 Transformers source checkout;
- V1 canary input;
- V1 R53-derived prefix-fixture plan;
- V1 review pack and raw authority.

Do not redownload the model unless the exact local asset is missing or hash-invalid.

Do not rerun V1 fallback science.

---

# 2. Isolated V1R1 environment

Create a new V1R1 isolated environment or a clean derivative of the V1 env.

Do not mutate the accepted V1 environment.

Pin:
- the same Transformers commit;
- a compatible PyTorch/CUDA combination;
- `kernels==0.17.0` unless the exact pinned Transformers source proves a different compatible 0.17.x version is required.

The key objective is to avoid the V1 CUDA build mismatch by using the Transformers Hub-kernel path rather than compiling `causal-conv1d` or `flash-linear-attention` locally.

Do not install local `causal-conv1d` or `flash-linear-attention` as the first V1R1 path.

Do not change system CUDA or driver.

Create:
`R54_V1R1_ENVIRONMENT_RECEIPT.json`

Record:
- Python;
- torch;
- torch CUDA;
- driver;
- system CUDA;
- Transformers commit;
- kernels version;
- all relevant package hashes/versions;
- environment path.

---

# 3. Hub-kernel provenance closure

Before model execution, inspect and record the resolved Hub-kernel repositories/revisions/artifacts used by `kernels==0.17.0`.

For the four GDN functions, record:
- operation name;
- Hub repo;
- layer/function name;
- resolved revision/version;
- downloaded source/binary hash;
- cache path;
- device compatibility;
- whether the mapping was actually selected.

No unpinned changing remote source may enter a formal run.

If the `kernels` package does not expose the resolved revision directly, capture the downloaded repository commit/metadata and hash the materialized files.

Create:
`HUB_KERNEL_PROVENANCE.tsv`.

---

# 4. Fast-path canary

Use the exact V1 Qwen3.5 model revision and the same bounded text-only input class.

Load with:

`use_kernels=True`

Use only documented/required trust flags for the resolved kernel repositories.

Run one prefill canary and one single-token continuation/decode canary.

Required evidence:

1. no GDN fallback warning for the targeted functions;
2. exact source/runtime mapping says the four functions are kernelized where they are exercised;
3. NSYS contains non-reference kernel strata attributable to the Hub kernels;
4. the original PyTorch fallback sequence is not the GDN primary path;
5. model output is finite;
6. model/cache structure remains valid.

Create:
- `R54_V1R1_FASTPATH_RECEIPT.json`
- `R54_V1R1_KERNEL_STRATA.tsv`

---

# 5. Numerical qualification against accepted V1 fallback

The optimized path need not be bitwise-identical internally, but it must preserve the frozen inference semantics.

Using the same V1 canary input compare fallback vs Hub-kernel path:

Required:
- exact output shape/dtype;
- no NaN/Inf;
- exact greedy argmax token;
- exact top-8 token-ID set;
- exact top1/top2 ordering.

Also record:
- max abs;
- mean abs;
- differing element count;
- output hashes.

Then run a fixed 16-token greedy continuation from the same prefix for both paths and require exact generated token IDs.

No post-hoc tolerance.

If semantic qualification fails:
`R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`

Do not continue to checkpoint timing.

---

# 6. Fast-path qualification decision

Emit one intermediate state:

### `R54_V1R1_HUB_FASTPATH_QUALIFIED`

Requires:
- actual Hub kernels on SM89;
- GDN fallback bypassed for the exercised path;
- semantic qualification passes.

Then automatically continue Phase 7.

### `R54_V1R1_HUB_FASTPATH_NOT_AVAILABLE`

Use if:
- Hub kernels cannot load/compile/run on SM89;
- mapping resolves to fallback;
- kernel artifact is incompatible.

### `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`

Use if optimized path changes the frozen discrete inference semantics.

For either negative state:
- update R54 review pack with V1R1 addendum;
- classify R54 current-platform runtime as not qualified;
- no further R54 performance science;
- STOP after publication closure.

Do not try a fourth unrelated fast-path stack.

---

# 7. Resume original R54 contract if qualified

If and only if:
`R54_V1R1_HUB_FASTPATH_QUALIFIED`

resume the original R54 measurement contract already committed in:

`docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/R54_MEASUREMENT_CONTRACT_V1.md`

and original long-horizon Goal:

`docs/vm_tlb/chatgpt_handoff/awma/r54_long_horizon_v1/CODEX_GOAL_109_R54_LONG_HORIZON_V1.md`

Scientific sequence to resume:

1. construct frozen prefix fixture;
2. exact runtime state-schema authority;
3. restore semantic canary;
4. M0/P0 baseline qualification;
5. P1/P2 checkpoint implementations;
6. P0/P1/P2 D512/D2048 formal production timing;
7. restore timing;
8. amortization N=1,2,4;
9. conditional holdout;
10. conditional NCU;
11. closest-work gate;
12. final R54 decision.

Do not alter:
- chunk=512;
- D512/D2048;
- 5% + 3x-jitter gates;
- prefix/suffix definitions;
- holdout rule;
- final-state definitions.

The only scientific change versus V1 is the qualified runtime backend.

---

# 8. Publication

If V1R1 fails at the fast-path gate, use:

`docs/vm_tlb/review_packs/AWMA_R54_FASTPATH_REQUALIFICATION_V1R1/`

If V1R1 qualifies and the full R54 experiment resumes, keep the full science in:

`docs/vm_tlb/review_packs/AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R1/`

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r54_fastpath_requal_v1r1_20260927/`

If full R54 resumes, larger raw may use a `full_r54/` subdirectory under the same authority.

Required V1R1 minimum:
- README.md
- V1_INHERITANCE.md
- R54_V1R1_ENVIRONMENT_RECEIPT.json
- HUB_KERNEL_PROVENANCE.tsv
- R54_V1R1_FASTPATH_RECEIPT.json
- R54_V1R1_KERNEL_STRATA.tsv
- R54_V1R1_SEMANTIC_EQUIVALENCE.tsv
- R54_V1R1_DECISION.md
- FINAL_DECISION.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

If full R54 resumes, include all original R54 measurement-contract deliverables as well.

Closure:
`science/engineering -> node164 -> review pack -> hashes -> commit -> push -> fetch-back -> exact remote SHA/tree verification -> clean worktree -> GPU lock released -> STOP`

No auto merge.

Git transport failure is publication-only; never rerun science because push fails.
