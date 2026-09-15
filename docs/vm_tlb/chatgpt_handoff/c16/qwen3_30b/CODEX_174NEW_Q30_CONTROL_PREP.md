# CODEX Goal — 174-new Qwen3-30B Control Preparation

## Role

CPU/storage/control-plane preparation only. Do not run GPU workloads.

## Inputs

Canonical model authority:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Accepted archive commit:

```text
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1
```

Read first:

```text
CURRENT_STATE_AFTER_Q30_ARCHIVE.md
Q30_EXECUTION_PREP_CONTRACT_V1.md
```

## Goal

Prepare all CPU-side authority required so node109 can immediately provision/run semantic layer streaming without inventing metadata during GPU work.

### Required work

1. Build `Q30_MODEL_LAYOUT.tsv` from exact index + safetensors headers.
2. Map all 18,867 indexed tensor keys to component/layer/expert classes where derivable.
3. Produce per-layer and per-expert byte totals and exact tensor manifests.
4. Identify exact tensors for embedding, each complete decoder layer, final norm and lm_head.
5. Freeze the baseline runtime requirements from archived config/model type and source compatibility.
6. Build prospective Qwen3 input bindings for at least Q30_S0_TEXT, Q30_S1_CODE, Q30_S2_TEXT, Q30_S2_CODE, Q30_S2_STRUCTURED using the pinned Qwen3 tokenizer authority.
7. Reuse prior C16 raw semantic payloads where available, but never reuse Qwen2 token IDs.
8. Store exact token IDs and binding receipts under node164 provenance/assets input namespace without placing them in current captures/raw.
9. Produce a node109 provisioning manifest referencing the canonical model receipt/inventory.
10. Create a `Q30_EXECUTION_PREP_PLAN.json` consumable by node109.

### Input binding rules

- Exact token IDs are the future execution authority.
- Record raw payload SHA, construction rule, tokenizer SHA, token IDs SHA and actual length.
- If deterministic repetition/truncation is needed, record it explicitly.
- Do not silently alter semantic class.
- Do not create S3/S4 unless S0/S1/S2 bindings are cleanly closed first.

### Model-layout fail-closed rules

Block only the affected mapping if:

```text
index key absent from safetensors headers
header key not represented by index
ambiguous layer/expert mapping that cannot be proven
required runtime tensor not represented in canonical payload
```

Unknown semantic role may remain `OTHER/UNKNOWN` if tensor identity/layer ownership remains exact.

### Deliverables

Create review pack:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_CONTROL_PREP_174NEW_V1/
```

Include at least:

```text
README.md
Q30_MODEL_LAYOUT.tsv
Q30_LAYER_SUMMARY.tsv
Q30_EXPERT_SUMMARY.tsv
Q30_COMPONENT_SUMMARY.tsv
Q30_INPUT_BINDINGS.tsv
Q30_INPUT_BINDING_RECEIPTS.tsv
Q30_RUNTIME_REQUIREMENTS.json
Q30_NODE109_PROVISIONING_MANIFEST.tsv
Q30_EXECUTION_PREP_PLAN.json
OPEN_ISSUES.md
SHA256SUMS
```

Expected final status:

```text
Q30_CONTROL_PREP_PASS
```

Do not run GPU, do not copy 61GB to node109, do not start layer streaming, NCU or NVBit.

Commit/push and STOP.
