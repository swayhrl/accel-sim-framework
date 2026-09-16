# Qwen3-30B-A3B S2 State Expansion — Current State V1

## Accepted scientific state

The Qwen3-30B-A3B deployment has passed exact S0 semantic streaming, real target-state freezing, complete Layer-24 replay, and S0 layer-local target qualification.

Accepted model identity:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Accepted execution deployment:

```text
qwen3_30b_a3b_hf451_bf16_sdpa_qwen3moe_sparse_expert_loop
```

Accepted semantic/replay commit:

```text
ba4358b8059be4fb5756f49852e50ecfe7dea9a3
```

Accepted S0 target-qualification commit:

```text
acbda39f5714cedb0e8b88ec32b07b4db2845885
```

Accepted S0 final state:

```text
QWEN3_30B_READY_FOR_LAYER_LOCAL_PROFILING
```

This readiness currently applies to the validated S0/T128 Layer-24 replay states and their qualified layer-local/kernel-local targets.

## Accepted S0 qualified targets

```text
Q30_PF_ATTENTION_FLASH          PREFILL   ATTENTION                       layer24 ordinal 48   23 static GLOBAL MREFs
Q30_PF_EXPERT_GEMM              PREFILL   EXPERT_PROJECTION_OR_GEMM       layer24 ordinal 96   47 static GLOBAL MREFs
Q30_DEC3_ATTENTION_SPLITKV      DECODE    ATTENTION                       layer24 ordinal 47   57 static GLOBAL MREFs
Q30_DEC3_EXPERT_GEMV            DECODE    EXPERT_PROJECTION_OR_GEMM       layer24 ordinal 202  243 static GLOBAL MREFs
```

These identities are S0-specific qualification evidence. Do not assume their launch ordinals, shapes, function occurrence identity, or static MREF sets remain valid under S2/T2048.

## Why S2 is required before formal capture

The accepted S0 qualification explicitly recommended generating and validating an exact S2/T2048 replay state before formal NCU/NVBit capture.

S0/T128 proves the semantic families, runtime path, replay procedure and tool chain. It does not establish:

```text
long-context Prefill attention shape
long-context Decode KV shape
T2048 routed-expert token distribution
T2048 expert working-set coverage
whether the same CUDA kernel variants remain selected
whether exact launch ordinals/grid/block remain stable
whether static GLOBAL-MREF sets remain unchanged
```

Therefore the next stage is state generation and exact replay only. S2 target requalification is a later separate gate.

## Preserved node109 authorities

Expected local model:

```text
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Expected local runtime:

```text
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Existing S0 bring-up data:

```text
/data/c16/qwen3_30b/bringup/Q30_S0_STREAM_V1_20260916T045044Z/
```

Node164 canonical model authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

## Frozen S2 input authority

Use only:

```text
Q30_S2_TEXT
class: TEXT
B1
context: 2048
prospective decode budget: 32
actual frozen input tokens: 2048
```

Node164 token-id authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
Q30_S2_TEXT.token_ids.json
```

Expected SHA256:

```text
00d47e2312fb3db3585b5396ebc7484507356148019a845c8253c6d58d56d4f5
```

Receipt:

```text
Q30_S2_TEXT.receipt.json
```

Expected receipt SHA256:

```text
e3368d01dc311d134e1f62c6412a3c05b2a2fb1de527f1947f3b7502af28c99a
```

Do not retokenize or reconstruct the S2 input.

## Bounded execution slice for this Goal

The parent Q30_S2_TEXT binding allows 32 Decode steps. This Goal intentionally executes only the prefix required to create a directly comparable long-context replay canary:

```text
Prefill: full T2048
Decode: steps 0,1,2,3 only
```

Classify this execution slice explicitly as:

```text
Q30_S2_TEXT_PREFIX_D4
parent_binding = Q30_S2_TEXT B1/T2048/D32
```

This is not a new token binding. It is a bounded execution prefix over the frozen D32 authority.

The fixed replay canaries remain:

```text
PREFILL layer 24
DECODE step 3 layer 24
```

This preserves direct comparability with S0.

## Scientific boundary

This stage may establish exact S2/T2048 semantic state and complete-layer replay.

It does not yet authorize formal capture.

After this stage, S2 replay must still undergo:

```text
kernel census
semantic occurrence re-identification
bounded NCU qualification
NVBit static GLOBAL-MREF remapping
```

before any formal dynamic MREF-sharded trace begins.
