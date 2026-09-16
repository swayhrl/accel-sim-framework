# CODEX Goal — Q30 S2/T2048 Layer-Local Target Requalification V1

## Objective

Use the already accepted exact S2/T2048 Layer-24 replay states to requalify the memory-important layer-local target kernels on RTX4080, compare them directly against the accepted S0/T128 qualification, and freeze an evidence-backed final portfolio for a later formal NCU/NVBit capture campaign.

This Goal ends **before formal capture**.

Expected successful decision:

```text
Q30_S2_LAYER_LOCAL_TARGET_REQUALIFICATION_PASS
FORMAL_CAPTURE_NOT_STARTED
```

A successful Goal must produce exact S2 occurrence identities, static GLOBAL-MREF maps, bounded NCU evidence, S0-vs-S2 deltas, and a final formal-capture plan. It must not produce the final large dynamic trace dataset.

---

# 0. Bind upstream authority

Required accepted commits:

```text
S0 semantic/replay:
ba4358b8059be4fb5756f49852e50ecfe7dea9a3

S0 target qualification:
acbda39f5714cedb0e8b88ec32b07b4db2845885

S2/T2048 semantic state/replay:
ee67225edc8fc5868de585d38e0391cbeb755d9f
```

Verify `SHA256SUMS` for both accepted review packs before qualification:

```text
docs/vm_tlb/review_packs/C16_QWEN3_30B_S0_TARGET_QUALIFICATION_109_V1/
docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1/
```

If accepted evidence is corrupted or missing, STOP rather than silently regenerating or substituting it.

---

# 1. Platform, lock, deployment, and state revalidation

Before profiler/GPU actions:

```text
record hostname/user/date
record nvidia-smi GPU name/UUID/driver/memory/processes
verify expected RTX4080 UUID
inspect /data/c16/locks/c16_gpu_campaign.lock
acquire the lock normally
never kill/bypass another workload
```

Revalidate the preserved deployment:

```text
model:
/data/c16/models/qwen3-30b-a3b/
ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/

runtime:
/data/c16/env/c16-qwen3-30b-hf451-gpu
```

Do not upgrade/reinstall when authority still closes.

Revalidate the two S2 target states and one ordinary replay each before profiler work:

```text
PREFILL / Layer24 / T2048
DECODE step3 / Layer24
```

Require source/router bitwise closure to remain PASS. If an accepted local state bundle is absent, restore it from the accepted node164 provenance with exact file-set/size/SHA validation. Do not rerun the full 48-layer S2 semantic stream solely to recreate an intact archived state.

---

# 2. Complete S2 kernel census

Run a complete diagnostic kernel census separately for the exact S2 Prefill Layer-24 replay and S2 Decode-step3 Layer-24 replay.

NSYS/NVTX is authorized for this diagnostic purpose.

Requirements:

1. preserve the exact accepted layer replay semantics;
2. mark/consume official runtime submodule ranges where available;
3. enumerate every CUDA kernel launch in order;
4. record at least:

```text
phase
launch ordinal
kernel/function name
semantic NVTX range / module attribution
grid dimensions
block dimensions
shared memory if available
stream
start/duration (diagnostic only)
```

5. classify launches conservatively into:

```text
ATTENTION
ROUTER
EXPERT_PROJECTION_OR_GEMM
DISPATCH_OR_INDEXING
COMBINE_OR_REDUCTION
NORM_RESIDUAL
OTHER
```

Do not classify by kernel-name substring alone when NVTX/module evidence can disambiguate the launch.

The census must explicitly compare S2 with the accepted S0 census:

```text
same semantic family?
same exact function?
same launch ordinal?
same grid/block?
same number of family launches?
new/removed kernel variants?
```

---

# 3. Candidate selection policy

Start from semantic families, not from inherited S0 ordinal assumptions.

Required families to investigate:

```text
S2 Prefill Attention
S2 Prefill Expert compute / weight path
S2 Decode-step3 Attention/KV
S2 Decode-step3 Expert compute / weight path
```

Router/dispatch/combine may be retained only if S2 evidence shows an independently material memory behavior worthy of capture.

For each family choose at most a small bounded candidate set based on actual S2 census evidence. Prefer the occurrence that is:

```text
inside the exact Layer24 semantic range
stable across repeated replay
memory-important by bounded counters
semantically attributable
reachable by NVBit instrumentation
```

Do not select a target solely because it has the longest duration.

---

# 4. Exact occurrence stability

For every candidate, replay the same accepted state enough times to confirm the occurrence can be located deterministically.

Bind each occurrence using multiple independent identity fields:

```text
scenario/state manifest SHA
phase
layer id
decode step if applicable
semantic family
launch ordinal within exact replay
exact function name
grid/block
runtime/deployment identity
code-object/module/function identity where observable
```

A name-only target is not accepted.

If launch ordinal is not stable but another exact identity combination is stable, document and use the stronger selector. If no stable selector exists, the candidate is not qualified for formal capture.

---

# 5. Bounded NCU characterization

Run bounded NCU characterization only on the short candidate set.

Use the same or directly comparable metric authority as S0 qualification. At minimum preserve enough evidence to compare:

```text
DRAM read/write bytes or sectors
L2 read/write traffic / hit behavior where available
L1/TEX traffic where relevant
SM activity / throughput indicator
kernel duration as diagnostic only
launch identity and grid/block
```

Store `.ncu-rep` on the data plane and record SHA/path in Git review evidence.

Do not launch a broad all-kernel NCU campaign.

For each candidate create a direct S0-vs-S2 comparison with explicit caveats when the exact kernel implementation changed.

Key questions to answer:

```text
Does Prefill attention traffic/shape materially change at T2048?
Does Decode attention/KV traffic scale with the ~16x larger cache state?
Does Prefill expert traffic/working set change with 75 -> 92 unique experts and 1,024 -> 16,384 assignments?
Does Decode expert GEMV remain effectively the same shape/family or change implementation?
```

---

# 6. RTX4080-local NVBit static GLOBAL-MREF mapping

For each retained S2 candidate, build an RTX4080-local static GLOBAL memory-reference map using the accepted NVBit qualification tooling.

Record at least:

```text
exact function/code-object identity
static instruction index / PC identity according to tool contract
opcode
memory space
read/write/atomic classification
access width if provable
full static GLOBAL-MREF set
static MREF count
```

Do not inherit the S0 static-MREF set.

Then run a tiny reachability canary for at least one selected static GLOBAL MREF from each retained candidate to prove that:

```text
exact candidate occurrence is selected
callback executes
terminal close succeeds
overflow/drop = 0
```

This is qualification only. Do not run the complete dynamic MREF-sharded trace set in this Goal.

---

# 7. S0 vs S2 qualification delta

Produce a single authoritative comparison table containing, for each semantic family:

```text
S0 target ID
S2 target ID
scenario/context
phase
exact function identity
launch ordinal
grid/block
static GLOBAL MREF count
static MREF set relation if comparable
NCU DRAM traffic
NCU L2 traffic / hit metric
other key memory metric
semantic-state scaling context
interpretation
```

For static MREF sets, distinguish:

```text
EXACT_SAME_SET
SAME_FUNCTION_DIFFERENT_SET
DIFFERENT_FUNCTION_NOT_DIRECTLY_COMPARABLE
UNKNOWN
```

Do not force a set comparison across different code objects/functions.

The interpretation must remain layer/kernel-local. Do not infer full-model cache/TLB behavior.

---

# 8. Freeze the final formal-capture portfolio

At the end of requalification, freeze a small final portfolio for the later formal campaign.

The default ceiling is **4–6 formal targets total across S0 and S2**, unless strong evidence justifies more.

For every potential target classify it as one of:

```text
FORMAL_CAPTURE_SELECTED
REFERENCE_ONLY
DROPPED_REDUNDANT
DROPPED_UNSTABLE
DROPPED_LOW_MEMORY_VALUE
```

Selection must be evidence-based.

The portfolio should answer whether each semantic family is best represented by:

```text
S0 only
S2 only
both S0 and S2
```

Guidance, not a forced conclusion:

- Prefill Attention is likely to require S2 if kernel shape/traffic materially changes with context.
- Decode Attention/KV is likely to require S2 if long-KV traffic differs materially.
- Prefill Expert may warrant both only if S2 routed-expert expansion produces materially different target behavior not captured by one state.
- Decode Expert should not be duplicated across S0/S2 if the same kernel/shape/static map and bounded memory behavior are effectively redundant.

Do not encode these as predetermined results; use measured evidence.

For each `FORMAL_CAPTURE_SELECTED` target freeze:

```text
target_id
scenario/state authority
phase/layer/decode step
semantic family
exact occurrence selector
function/code-object identity
grid/block
full static GLOBAL-MREF list and count
bounded NCU evidence SHA
NVBit static-map SHA
one-MREF canary receipt SHA
recommended formal capture mode
claim scope
```

Recommended formal NVBit mode should normally be:

```text
MREF_SHARDED_COMPLETE_SET
```

unless candidate-specific evidence shows CTA sharding is more appropriate. State the reason.

Also estimate the formal shard count and expected operational cost from the static MREF count so the next Goal can be scheduled sensibly.

---

# 9. Formal capture readiness decision

PASS requires:

```text
accepted S2 states revalidated
complete S2 Layer24 replay census for Prefill and Decode3
memory-important candidates selected without inherited-ordinal assumption
bounded NCU characterization complete
S2 static GLOBAL-MREF maps complete
one-MREF reachability canaries terminal-close
S0-vs-S2 delta table complete
final 4–6 target capture portfolio frozen
all selected targets have stable exact occurrence selectors
```

Expected final decision:

```text
Q30_S2_LAYER_LOCAL_TARGET_REQUALIFICATION_PASS
Q30_FORMAL_LAYER_LOCAL_CAPTURE_PLAN_READY
FORMAL_CAPTURE_NOT_STARTED
```

Do not use `Q30_FORMAL_LAYER_LOCAL_CAPTURE_PLAN_READY` if any selected target still lacks a stable occurrence identity or complete static MREF set.

---

# 10. Explicitly out of scope

Do not in this Goal:

```text
run full dynamic MREF-sharded complete-set traces
run large all-MREF NVBit payload capture
run broad formal NCU matrix
admit anything into Pipeline V1 raw/catalog
run S2_CODE or S2_STRUCTURED
run additional full-model semantic scenarios
make full-model resident performance/cache/TLB claims
```

Diagnostic replay, NSYS census, bounded NCU, static NVBit mapping, and one-MREF canaries are authorized.

---

# 11. Required review pack

Create:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_S2_TARGET_REQUALIFICATION_109_V1/
```

Include at least:

```text
README.md
UPSTREAM_AUTHORITY.tsv
PLATFORM_AND_TOOL_AUTHORITY.json
S2_REPLAY_STATE_REVALIDATION.tsv
S2_PREFILL_KERNEL_CENSUS.tsv
S2_DECODE3_KERNEL_CENSUS.tsv
S2_SEMANTIC_LAUNCH_MAP.tsv
S2_CANDIDATE_MATRIX.tsv
S2_OCCURRENCE_STABILITY.tsv
S2_NCU_CHARACTERIZATION.tsv
S2_NCU_ARTIFACT_INDEX.tsv
S2_NVBIT_STATIC_MREF_MAP.tsv
S2_NVBIT_REACHABILITY.tsv
S0_VS_S2_TARGET_DELTA.tsv
FINAL_FORMAL_CAPTURE_PORTFOLIO.tsv
FORMAL_CAPTURE_COST_ESTIMATE.tsv
OPEN_ISSUES.md
FINAL_DECISION.json
SHA256SUMS
```

Do not put large profiler binaries or traces in Git; record their data-plane paths and SHA256.

---

# 12. Cleanup and STOP

After qualification:

```text
commit
push
release GPU lock
verify no profiler/Q30 CUDA process remains
verify GPU returns to driver baseline
report final branch/SHA/status
report S2 target identities and S0-vs-S2 deltas
report final selected formal portfolio
report estimated shard counts/cost
STOP
```

Do not automatically continue into formal capture.