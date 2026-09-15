# C16 Qwen3-30B-A3B — CPU Streaming Implementation Prep Current State V1

Status: `CONTROL_PREP_CLOSED / GPU_EXECUTION_NOT_STARTED`

This handoff is for a fresh 174-new Codex window. Do not assume any prior chat context.

## 1. Accepted authorities

Model identity:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Canonical asset acceptance:

```text
branch: hrl/c16-qwen3-30b-asset-archive-exec-v2
commit: d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
status: QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

Canonical node164 path:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Accepted payload facts:

```text
16 BF16 safetensors weight shards
61,066,575,648 weight bytes
10 exact-revision non-weight authority files
26 canonical files total
61,084,187,391 canonical bytes total
18,867 index/header tensor keys
missing = 0
unindexed = 0
```

Control preparation acceptance:

```text
branch: hrl/c16-qwen3-30b-control-prep-174new-v1
commit: 674d7acda0aaf072b7cd12cac84da9264b559cb2
status: Q30_CONTROL_PREP_PASS
review pack:
docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

The control-prep pack is the immediate CPU-side authority for this stage.

## 2. Frozen CPU-side products already available

The accepted control-prep pack contains:

```text
Q30_MODEL_LAYOUT.tsv
Q30_LAYER_SUMMARY.tsv
Q30_EXPERT_SUMMARY.tsv
Q30_COMPONENT_SUMMARY.tsv
Q30_INPUT_BINDINGS.tsv
Q30_INPUT_BINDING_RECEIPTS.tsv
Q30_RUNTIME_REQUIREMENTS.json
Q30_NODE109_PROVISIONING_MANIFEST.tsv
Q30_EXECUTION_PREP_PLAN.json
```

Important accepted facts include:

```text
48 decoder layers
18,867 mapped model tensors
all 5 initial prospective Qwen3 input bindings frozen
node109 working-copy action NOT_STARTED
GPU action NOT_STARTED
```

Prospective input authority root:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Initial frozen scenarios:

```text
Q30_S0_TEXT        B1 / T128  / Decode4
Q30_S1_CODE        B1 / T256  / Decode16
Q30_S2_TEXT        B1 / T2048 / Decode32
Q30_S2_CODE        B1 / T2048 / Decode32
Q30_S2_STRUCTURED  B1 / T2048 / Decode32
```

## 3. Node109 state boundary

Node109 is currently occupied by another GPU capture campaign.

Therefore this stage MUST remain CPU-only on 174-new.

Do not:

```text
copy the 61 GB model to node109
write to /data/c16 on node109
run any GPU workload on node109
start CUDA on node109
acquire or bypass the node109 GPU campaign lock
run Qwen3 semantic streaming on RTX4080
run NCU / NVBit / NSYS
```

The purpose of this stage is to move implementation/debug work off the critical GPU path so that, once node109 becomes free, the remaining work is primarily provisioning plus bounded GPU validation.

## 4. Scientific route that must remain unchanged

The planned execution route remains:

```text
canonical BF16 asset
    -> node109 local exact working copy
    -> exact semantic layer streaming
    -> freeze TARGET_LAYER_STATE
    -> exact full-layer replay canary
    -> representative NCU
    -> MREF-sharded complete-set NVBit
```

This CPU-prep stage must not weaken the scientific identity. In particular, it must not create a substitute model or reimplement Qwen3 mathematical semantics independently from the exact runtime.

Forbidden substitutions include:

```text
expert pruning
reduced expert count
changed router top-k
quantization used as BF16 authority
synthetic target-layer inputs used as formal evidence
custom attention/MoE math that bypasses the frozen runtime implementation
full-model performance claims from layer streaming
```

## 5. What this stage should accomplish

Prepare production-quality, CPU-tested implementation and contracts for:

```text
canonical authority loading/validation
exact tensor/module mapping
per-layer materialization plans
shard-aware tensor loading
semantic-streaming runner structure
KV/state movement interfaces
TARGET_LAYER_STATE schema + serializer/validator
exact-layer replay harness structure
node109 working-copy provisioning tool
node109 runtime bootstrap/lock
CPU synthetic Qwen3-MoE equivalence tests
```

No real Qwen3-30B GPU execution is required or authorized here.

## 6. End-state of this CPU stage

Successful completion should mean:

```text
Q30_CPU_STREAMING_IMPLEMENTATION_PREP_PASS
```

with an explicit boundary:

```text
GPU_VALIDATION_NOT_STARTED
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING = NOT YET
```

The next node109 stage will still have to prove S0 semantic streaming and exact full-layer replay on the RTX4080 before formal profiling is authorized.
