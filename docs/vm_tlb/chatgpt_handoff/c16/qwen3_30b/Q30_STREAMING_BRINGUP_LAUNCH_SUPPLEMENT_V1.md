# Q30 Streaming Bring-up Launch Supplement V1

Status: execution supplement for the node109 Qwen3-30B streaming bring-up. This document binds the earlier bring-up Goal to the now-accepted CPU/control authority and adds start-time coordination rules.

## Accepted authorities

Canonical model asset:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Canonical archive closeout:

```text
branch: hrl/c16-qwen3-30b-asset-archive-exec-v2
commit: d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
status: QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

Accepted control-prep authority:

```text
branch: hrl/c16-qwen3-30b-control-prep-174new-v1
commit: 674d7acda0aaf072b7cd12cac84da9264b559cb2
status: Q30_CONTROL_PREP_PASS
review pack: docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

Key frozen control objects:

```text
Q30_MODEL_LAYOUT.tsv            sha256 c0d9dc9615762d68a1d47c91a42585195eff4f9f23071a349535b5ca489b3e52
Q30_INPUT_BINDINGS.tsv          sha256 5435b7fafd3457e527e21e2c576431a8e405d871b8ff21eccce500ecbbed2dfd
Q30_INPUT_BINDING_RECEIPTS.tsv  sha256 4e07b8275d5a89583eaf055718114a13cd7f9adb4534cecacd12f58bd558c497
Q30_LAYER_SUMMARY.tsv           sha256 1cac7f2fcdc2184307e679aba1bad5d13895e4acd27a464e63b68c84f7f18635
Q30_NODE109_PROVISIONING_MANIFEST.tsv sha256 6fd6ddcbb801347fec72061976f0f9464a9cc4311b1e8981a5d2670d062bcdca
Q30_RUNTIME_REQUIREMENTS.json   sha256 18005cf38cafeb23b2d7a109a9de9e77d596aa333ee262d1e646f0b6a187571a
Q30_EXECUTION_PREP_PLAN.json    sha256 98b0d1e1bfdcfa5293047a7964833e9874d4f6c7e58790e9fc5b7c77d684ac16
```

The five prospective pinned-tokenizer scenarios are:

```text
Q30_S0_TEXT        B1 T128  Decode4
Q30_S1_CODE        B1 T256  Decode16
Q30_S2_TEXT        B1 T2048 Decode32
Q30_S2_CODE        B1 T2048 Decode32
Q30_S2_STRUCTURED  B1 T2048 Decode32
```

Only `Q30_S0_TEXT` is authorized for the first semantic streaming/replay bring-up. Do not expand to the other scenarios until S0 closes.

## Start-time coordination

Do not begin node109 provisioning or runtime setup while another scientific capture on node109 is actively producing timing/trace evidence if the 61 GB copy, hashing, package installation, or filesystem activity could perturb that campaign.

Before starting this Goal:

1. confirm the current node109 scientific GPU/capture task is complete or at a safe STOP boundary;
2. confirm `/data/c16/locks/c16_gpu_campaign.lock` is free before any GPU action;
3. confirm sufficient `/data/c16` free space for the 61,084,187,391-byte working copy plus temporary `.partial`, runtime environment, TARGET_LAYER_STATE objects, and capture headroom;
4. do not remove any existing C16 model/capture data merely to make space without an explicitly authorized cleanup decision;
5. preserve the original Qwen3-30B download source until the node109 working copy is independently hash-closed.

## Node109 working copy

Provision exactly:

```text
source:
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/

destination:
/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Use the accepted provisioning manifest. Required lifecycle:

```text
.partial
-> resume-capable content copy
-> independent regular-file set / size / SHA256 verification
-> no-overwrite promotion
-> WORKING_COPY_RECEIPT.json
```

The source canonical archive remains read-only.

## Runtime identity

Create a dedicated runtime; do not mutate the existing C16 Llama/Qwen2 environment in place. The actual Qwen3 MoE runtime implementation is part of deployment identity.

The first deployment must be conservative and explicitly named, e.g.:

```text
qwen3_30b_a3b_hf_baseline_bf16
```

Use the exact archived config and compatible baseline Transformers path. Do not silently enable a newer grouped/fused MoE implementation merely because it is available. If a different implementation is intentionally evaluated later, it is a separate deployment.

## Semantic streaming acceptance focus

The Goal is not to make the 61 GB model appear to fit the RTX4080. It is to prove that exact per-layer semantics can be reconstructed with simultaneous-residency decoupled from model semantics.

Required S0 evidence:

```text
exact BF16 tensors
all 48 layers
all experts preserved
original router/top-k behavior
exact attention/KV semantics
per-layer hidden-state receipts
router/expert assignment summaries
bounded peak GPU memory
prefill semantic completion
decode semantic completion
```

Freeze at least one Prefill and one Decode `TARGET_LAYER_STATE` after semantic execution.

## Exact replay acceptance

For each selected replay state, execute the complete exact layer, not a synthetic standalone GEMM. Require:

```text
streaming-source layer output == replay layer output
router selections == replay router selections
expert token counts == replay expert token counts
repeat replay deterministically
```

Use byte/hash equality where serialization permits exact byte-stable comparison; otherwise use an explicitly justified numerical equality gate that is strict enough to detect semantic drift and record why byte equality is unavailable.

Final gate remains:

```text
Q30_EXACT_LAYER_REPLAY_CANARY_PASS
```

and final stage status:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

Do not begin large NCU/NVBit capture in this bring-up Goal.

## Recovery policy

Engineering problems are sub-goals, not immediate STOP reasons:

```text
package/runtime incompatibility -> isolate and pin compatible runtime
loader/shard mapping issue -> return to exact index/layout authority
single-layer OOM -> verify stale processes/allocator state; do not prune experts or change precision
state serialization mismatch -> repair state schema and regenerate only affected state
KV/cache-position mismatch -> repair exact state handling
router mismatch -> inspect exact module/runtime path and tensor mapping
```

Do not lower model, input, dtype, backend, routing, expert-count, context, or layer-completeness standards to get a PASS.

## Source cleanup boundary

The original completed download root:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

must remain untouched in this Goal. A later cleanup may be authorized only after both node164 canonical archive and node109 local working copy are independently closed.
