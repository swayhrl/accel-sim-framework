# C16 Qwen3-30B-A3B — Current State After Canonical Archive

Status: `ASSET_CLOSED / EXECUTION_NOT_STARTED`

## Canonical model authority

Model:

```text
Qwen/Qwen3-30B-A3B
revision: ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Accepted archive commit:

```text
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
```

Accepted status:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

Canonical node164 path:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Canonical payload:

```text
16 safetensors weight shards
61,066,575,648 weight bytes
10 exact-revision non-weight authority files
26 canonical files total
61,084,187,391 canonical bytes total
```

Index/header closure:

```text
weight-index tensor keys: 18,867
safetensors-header tensor keys: 18,867
matched: 18,867
missing: 0
unindexed: 0
referenced shards: 16
```

The source download remains intact and has not been deleted.

## Existing execution plan

The scientific route is frozen conceptually as:

```text
semantic layer streaming
    -> freeze exact target-layer state
    -> exact full-layer replay on RTX4080
    -> representative NCU
    -> MREF-sharded complete-set NVBit
```

The RTX4080 must not be used to fake full-model residency by changing the model.

Forbidden substitutions for BF16 authority include:

```text
expert pruning
reduced expert count
changed top-k
quantization used as BF16 substitute
CPU-offloaded target-layer profiling
Unified-Memory oversubscription used as memory-characterization evidence
changed context/batch/backend/precision merely to make the run fit
```

Host/disk staging is allowed for inactive layers during semantic-state reconstruction because the semantic streaming pass is not itself performance evidence.

## Evidence classification

Planned 4080 evidence is initially limited to:

```text
FORMAL_LAYER_LOCAL
FORMAL_KERNEL_LOCAL
```

It must not be called full-model-resident timing/cache/TLB evidence without a later full-resident calibration.

## Immediate next work

Before formal profiling:

1. provision a local node109 working copy through independent SHA closure;
2. build a prospective Qwen3-30B input authority using the pinned tokenizer;
3. freeze an isolated exact runtime/deployment identity;
4. derive a deterministic tensor->component->layer/expert layout from the canonical index;
5. implement and validate semantic layer streaming;
6. freeze exact target-layer state receipts;
7. prove exact full-layer replay equivalence for selected layers/steps;
8. only then start NCU/NVBit target qualification.

No large formal Qwen3-30B profiling has yet been authorized or performed.
