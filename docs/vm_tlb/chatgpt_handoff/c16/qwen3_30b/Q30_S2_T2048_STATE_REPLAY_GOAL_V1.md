# CODEX Goal — Qwen3-30B S2/T2048 Semantic State + Exact Replay V1

## Goal

Generate and validate an exact long-context Q30 replay authority before formal NCU/NVBit capture.

This Goal uses the already accepted Qwen3-30B BF16 deployment and frozen `Q30_S2_TEXT` input authority. It runs a full T2048 Prefill and only the first four Decode steps, freezes exact Layer-24 call-boundary states, proves fresh-process complete-layer replay equivalence, and records routed-expert/KV scaling evidence versus S0.

This Goal does **not** perform S2 kernel target qualification and does **not** begin formal capture.

Expected successful final state:

```text
Q30_S2_T2048_STATE_REPLAY_PASS
FORMAL_CAPTURE_NOT_YET_AUTHORIZED
```

---

# 0. Upstream authority

Consume and verify:

```text
asset archive:
d048d1a5348ff3ace248d1e62cdd8e071a82d5d1

control/input/layout prep:
674d7acda0aaf072b7cd12cac84da9264b559cb2

CPU streaming hardening:
6034071c76279952c1476626552a9eaaaab6ef0b

S0 semantic/replay:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3

S0 target qualification:
acbda39f5714cedb0e8b88ec32b07b4db2845885
```

Verify the relevant review-pack `SHA256SUMS` before scientific execution.

Do not change:

```text
model revision
BF16 precision
128 experts
top-k = 8
batch = 1
SDPA deployment
Qwen3 runtime implementation
```

---

# 1. Node109 resume preflight

Before GPU actions:

1. record hostname/user/date;
2. verify RTX4080 UUID `GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`;
3. record driver/CUDA state and active processes;
4. inspect `/data/c16/locks/c16_gpu_campaign.lock`;
5. acquire the lock normally before CUDA work;
6. do not kill/bypass any live workload.

Revalidate preserved local authorities rather than rebuilding them:

```text
model:
/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/

runtime:
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Expected working-copy authority:

```text
26 files
61,084,187,391 bytes
inventory SHA256:
20b21f889daf61d7362d4e0042ff7f3b2517cc1f0a917d3e0667654ded8cb30a
```

Expected runtime identity remains the accepted HF 4.51.0 BF16 SDPA Qwen3MoE sparse-expert-loop deployment unless revalidation disproves it.

Do not recopy 61 GB or reinstall the runtime when authority closes.

---

# 2. Provision frozen S2 input locally

Copy only the accepted `Q30_S2_TEXT` token-id artifact and receipt from node164 provenance to the existing local Q30 input namespace.

Expected source:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Expected token-id SHA256:

```text
00d47e2312fb3db3585b5396ebc7484507356148019a845c8253c6d58d56d4f5
```

Expected receipt SHA256:

```text
e3368d01dc311d134e1f62c6412a3c05b2a2fb1de527f1947f3b7502af28c99a
```

Do not retokenize.

Record local exact path/size/SHA closure.

Execution identity for this Goal:

```text
execution_scenario = Q30_S2_TEXT_PREFIX_D4
parent_binding = Q30_S2_TEXT B1/T2048/D32
executed_decode_steps = 0..3
```

The D4 prefix is not a new binding.

---

# 3. S2/T2048 real semantic Prefill

Run the exact accepted semantic streaming implementation over all 48 original decoder layers.

Input:

```text
B1
T2048
exact frozen Q30_S2_TEXT token IDs
```

Execution:

```text
embedding
→ layer 0
→ ...
→ layer 47
→ final norm
→ lm_head
→ greedy next token
```

For every layer, preserve original runtime semantics and use one exact complete BF16 layer at a time.

Record at least:

```text
layer id
input/output shape/dtype
output checksum/SHA receipt
materialized tensor count
materialized weight bytes
peak allocated/reserved
post-release allocated/reserved
KV shape/dtype/content receipt
router evidence
unique selected expert count
expert assignment histogram summary
```

For routed-expert evidence, record enough to compare S0 and S2 without storing giant per-token tables in Git. Large detailed artifacts may stay on the data plane with path/SHA references.

At minimum for Layer 24 record:

```text
number of token-expert assignments
number of unique experts selected
min/median/p95/max tokens per selected expert
expert-id bitmap/list SHA
assignment histogram SHA
```

This is semantic evidence, not performance evidence.

---

# 4. Freeze S2 Prefill Layer-24 state

Immediately before the exact complete Layer-24 forward during T2048 Prefill, freeze the real runtime call-boundary state.

Use the accepted hardened TARGET_LAYER_STATE schema and extend only if the actual runtime consumes additional kwargs.

The state must include all exact artifacts/identity needed for independent replay, including as applicable:

```text
hidden_states
attention mask identity/artifact
position_ids
cache_position
position embeddings / cos / sin
runtime tensor kwargs
model/runtime/input/source-run identity
```

Also preserve the corresponding semantic source layer output and router/expert oracle for comparison.

Do not select another layer post hoc.

Fixed canary:

```text
phase = PREFILL
layer_id = 24
context = 2048
```

---

# 5. Execute Decode prefix steps 0..3

Continue from the exact S2 Prefill KV state.

Perform exactly four deterministic greedy Decode forwards:

```text
step 0
step 1
step 2
step 3
```

For each step execute all 48 layers with exact per-layer KV restoration/update.

Record:

```text
generated token id
context length presented to attention
per-layer KV shape/dtype/content receipt
layer output receipt
router summary
unique selected experts per layer
peak allocated/reserved
```

Do not continue to steps 4..31 in this Goal unless required to diagnose a correctness problem. The accepted scientific slice is the first four Decode steps only.

---

# 6. Freeze S2 Decode step-3 Layer-24 state

Immediately before Layer-24 forward at zero-based Decode step 3, freeze the real exact call-boundary state.

Fixed canary:

```text
phase = DECODE
step = 3
layer_id = 24
parent Prefill context = 2048
```

Include exact layer-local past KV and every actual runtime tensor kwarg.

Preserve corresponding source output/router oracle.

---

# 7. Exact fresh-process complete-layer replay

For both S2 states:

```text
PREFILL Layer 24 T2048
DECODE step 3 Layer 24 after T2048 Prefill
```

run independent fresh-process complete-layer replay.

For each state:

1. instantiate exact accepted runtime layer on meta;
2. materialize all original BF16 Layer-24 weights and all experts;
3. restore exact state artifacts;
4. call the complete runtime layer;
5. compare with the semantic source oracle;
6. release layer;
7. repeat once from the same frozen state.

Require:

```text
output shape exact
output dtype exact
layer output bitwise equal by default
selected expert IDs exact
expert token counts exact
router evidence exact
replay1 == replay2
```

If bitwise equality fails, do not silently weaken tolerance. Produce detailed diagnostics and leave the Goal blocked for review.

Record actual peak GPU memory for both replays.

PASS gate:

```text
Q30_S2_EXACT_LAYER_REPLAY_PASS
```

---

# 8. S0 vs S2 semantic scaling comparison

Produce a compact comparison grounded only in accepted semantic evidence.

At minimum compare Layer 24:

```text
Prefill sequence length: 128 vs 2048
attention input shape
KV shape/bytes
router token-expert assignments
unique experts selected
expert assignment distribution summary
complete target-state size
replay peak memory
```

For Decode step 3 compare:

```text
S0 context length vs S2 context length
KV shape/bytes
attention call-boundary state shape
selected expert count
complete replay memory
```

Do not use these semantic quantities as substitutes for NCU/NVBit traffic measurements.

---

# 9. Preserve S2 replay authority

Keep large artifacts on node109 under a deterministic run root, e.g.:

```text
/data/c16/qwen3_30b/bringup/<S2_RUN_ID>/
```

After both replay canaries PASS, archive the selected S2 target-state bundles and small semantic/replay receipts to node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/
qwen3_30b_replay_states/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/<S2_RUN_ID>/
```

Use `.partial` + exact file-set/size/SHA verification + no-overwrite promotion.

Classification:

```text
REPLAY_STATE_PROVENANCE_ONLY_NOT_PIPELINE_RUN
```

---

# 10. Out of scope

Do not in this Goal run:

```text
NSYS census
NCU target qualification
NVBit static mapping
NVBit dynamic payload capture
MREF-sharded formal traces
S2_CODE
S2_STRUCTURED
Decode steps 4..31 unless debugging correctness
formal capture
```

Do not assume S0 launch ordinal/static-MREF identities transfer to S2.

---

# 11. Acceptance

PASS requires:

```text
Q30_S2_INPUT_LOCAL_AUTHORITY_PASS
Q30_S2_PREFILL_STREAMING_PASS
Q30_S2_DECODE_PREFIX_D4_PASS
Q30_S2_TARGET_LAYER_STATE_PASS
Q30_S2_EXACT_LAYER_REPLAY_PASS
Q30_S2_STATE_ARCHIVE_PASS
```

Final decision:

```text
Q30_S2_T2048_STATE_REPLAY_PASS
FORMAL_CAPTURE_NOT_YET_AUTHORIZED
```

The next stage after PASS is a separate S2 target-requalification Goal that must re-identify exact occurrences, shapes, NCU behavior and static GLOBAL-MREF maps before formal capture.

---

# 12. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
PLATFORM_PREFLIGHT.json
GPU_LOCK_RECEIPT.json
S2_INPUT_LOCAL_AUTHORITY.tsv
S2_EXECUTION_SUMMARY.tsv
S2_PREFILL_LAYER_SUMMARY.tsv
S2_DECODE_STEP_SUMMARY.tsv
S2_ROUTER_EXPERT_SUMMARY.tsv
S2_KV_SUMMARY.tsv
S2_TARGET_LAYER_STATE_INDEX.tsv
S2_EXACT_LAYER_REPLAY_CANARY.tsv
S2_REPLAY_DETERMINISM.tsv
S0_VS_S2_SEMANTIC_SCALING.tsv
S2_STATE_ARCHIVE_RECEIPT.tsv
GPU_MEMORY_SUMMARY.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Do not commit large hidden/KV/target-state binary payloads to Git.

After PASS:

```text
commit
push
release GPU lock
confirm GPU baseline/no Q30 process
report branch/SHA/status/review-pack
STOP
```
