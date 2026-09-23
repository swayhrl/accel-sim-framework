# C16 E1 Targeted CUDA L2-Persistence Intervention Design V1

## 1. Purpose

The preceding natural-reuse stage established:

- compressed AWQ q/down/up state can become effectively DRAM-light after one immediate reuse;
- realistic full-model decode interference destroys that isolated warm state;
- natural layer0/layer14 up_proj traffic becomes dense-like or beyond the isolated dense bracket;
- nominal capacity matters, but role/kernel/access-policy effects remain.

The next question is a direct real-hardware intervention:

> Can explicit CUDA persisting-L2 treatment of the dominant compressed qweight region preserve more of the target state across the real full-model token reuse interval?

This stage is a **policy intervention / mechanism-precondition experiment**.

It does not yet implement a new hardware replacement policy.

---

## 2. Accepted device capability

From accepted RTX4080 raw NCU device attributes:

- L2 bytes: `67,108,864`
- max persisting-L2 set-aside: `46,137,344`
- max access-policy window: `134,213,632`

These values must be re-queried from the runtime/device in the experiment and compared against accepted authority.

No value is silently assumed.

---

## 3. Target memory region

Default intervention granularity:

`exact qweight tensor storage only`

Reason:

- it is the dominant packed-weight object;
- it is one exact contiguous tensor/address interval;
- CUDA stream access-policy window is naturally defined over one address interval;
- using one min/max span across disjoint qweight/qzeros/scales could accidentally include unrelated allocations.

For accepted up_proj:

- qweight bytes = `33,947,648`
- total packed module state = `35,273,728`

The qweight region fits below the accepted max persisting-L2 set-aside.

The experiment must independently census exact qweight bytes/pointer/contiguity for:

- layer0 up_proj
- layer14 up_proj
- layer0 down_proj

Do not assume layer14 pointer layout from layer0.

If a target qweight tensor is not one exact contiguous storage interval, STOP that target rather than inventing a larger ambiguous window.

---

## 4. CUDA policy implementation

Use the installed CUDA runtime/driver support actually present on node109.

Intended APIs/capabilities:

- device persisting-L2 set-aside limit;
- stream access-policy window;
- persisting hit property;
- normal/streaming miss property as supported;
- context persisting-L2 reset between conditions.

Codex must inspect local headers/runtime first and record the exact implementation.

Do not assume API availability from external documentation alone.

### Required policy receipt

For every condition record:

- CUDA runtime version;
- device ordinal/name;
- queried L2 bytes;
- queried max persisting-L2 bytes;
- queried max access-policy-window bytes;
- requested set-aside bytes;
- actual/query-back set-aside bytes where supported;
- stream identity;
- access-policy base pointer;
- access-policy numBytes;
- hitRatio;
- hitProp;
- missProp;
- target qweight pointer/bytes;
- reset operation before/after condition.

---

## 5. Set-aside budget

Primary full-qweight condition:

- requested set-aside = exact target qweight bytes, rounded only if CUDA API/runtime requires alignment;
- access-policy window = exact qweight bytes;
- hitRatio = 1.0.

If the runtime rounds the accepted set-aside, preserve requested and actual values.

Never exceed the runtime-reported maximum.

---

## 6. Part A — policy qualification on isolated up_proj M1

Use the accepted TEXT layer0 up_proj M1 AWQ semantic replay.

Compare:

### ISO_BASELINE_DENSE
- reset persisting state;
- no persisting window;
- 2 target warmups;
- accepted 256 MiB DENSE_MEMORY_PRESSURE;
- target.

### ISO_QWEIGHT_PERSIST_DENSE
- reset;
- configure qweight persisting window;
- 2 target warmups;
- accepted 256 MiB DENSE_MEMORY_PRESSURE;
- target.

Native timing:
- 9 repetitions per condition;
- target only.

Semantic NCU:
- application replay;
- cache-control none;
- exact target NVTX;
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`

Qualification succeeds if:
- target identity/backend unchanged;
- policy receipt is valid;
- target qweight window is exact;
- NCU selector closes.

No minimum performance effect is required for engineering qualification.

Interpretation:
- a strong traffic reduction is positive evidence the policy is effective;
- no reduction means the natural experiment remains valid but policy effectiveness is uncertain and must be interpreted cautiously.

---

## 7. Part B — natural full-model persistence intervention

Use the accepted Qwen2.5-7B AWQ full-model sequence:

- accepted S2_TEXT 2048-token prefix;
- exactly 4 deterministic greedy decode steps;
- expected tokens remain `[23578, 11, 323, 3950]`;
- same occurrence targets:
  - layer0 up_proj
  - layer14 up_proj
  - layer0 down_proj.

### Conditions

Run five fresh-process conditions:

#### BASELINE
- persisting state reset;
- set-aside disabled/zero where supported;
- no access-policy window.

#### SETASIDE_ONLY
- reserve the same qweight-sized persisting-L2 budget;
- no target region receives persisting treatment;
- all target windows disabled/normal.

#### PERSIST_L0_UP
- same qweight-sized set-aside;
- exact layer0 up_proj qweight window marked persisting.

#### PERSIST_L14_UP
- same qweight-sized set-aside;
- exact layer14 up_proj qweight window marked persisting.

#### PERSIST_L0_DOWN
- same qweight-sized set-aside;
- exact layer0 down_proj qweight window marked persisting.

This design provides target and matched-other controls under the same reserved capacity.

### Native repetitions

For every condition:
- 7 fresh processes;
- exact same prefix/tokens;
- record all 12 occurrence input/output SHA;
- record target occurrence timings;
- record decode-step timings;
- record total prefill time if cheap and unambiguous.

Do not synchronize inside the normal model loop except what is required by the accepted event-based measurement method.

### Primary stable occurrences

Because layer0 D0 has an accepted first-step timing effect, primary policy comparisons are:

- layer0 up_proj D1 and D3;
- layer14 up_proj D3;
- layer0 down_proj D3.

D0 remains reported but is not the sole basis for a policy claim.

---

## 8. Natural NCU matrix

Use application replay + cache-control none.

Primary profile matrix:

### For layer0 up_proj
D1 and D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_UP
- PERSIST_L14_UP

### For layer14 up_proj
D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L14_UP
- PERSIST_L0_UP

### For layer0 down_proj
D3 under:
- BASELINE
- SETASIDE_ONLY
- PERSIST_L0_DOWN
- PERSIST_L0_UP

Maximum:
`8 + 4 + 4 = 16 natural semantic profiles`

Metrics:
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`

Optional unit-resolved L2 hit-rate/counter metrics may be collected only if:
- exact runtime metric name is queried;
- unit/meaning is preserved;
- they do not expand replay complexity materially.

They are not required.

For every NCU profile preserve:
- BASE.csv
- SESSION.csv
- PROFILE.log
- policy receipt
- target identity
- kernel inventory
- replay pass count.

---

## 9. Matched-control comparisons

For a target T, compare:

### Target persistence effect
`PERSIST_T vs SETASIDE_ONLY`

This isolates target-region treatment from merely reserving persisting-L2 capacity.

### Matched unrelated persistence effect
Example for layer0 up_proj:
`PERSIST_L14_UP vs SETASIDE_ONLY`

This tests whether persisting some same-sized compressed weight region generically changes the target.

### Baseline effect
`SETASIDE_ONLY vs BASELINE`

This measures whether the reservation itself perturbs target/full-model behavior.

Do not attribute `PERSIST_T vs BASELINE` entirely to target persistence unless these controls are also considered.

---

## 10. Materiality

For native target timing:

`MATERIAL_TIMING_BENEFIT`

if:
- target-persist median is at least 5% lower than SETASIDE_ONLY;
- and effect exceeds combined timing dispersion.

For target DRAM:

`MATERIAL_DRAM_BENEFIT`

if:
- target-persist DRAM is at least 20% lower than SETASIDE_ONLY;
- and absolute reduction is at least 4 MiB.

For control specificity:

`TARGET_SPECIFIC`

if:
- target-persist benefit is materially larger than the matched unrelated-persist effect for the same target.

These are scoped experiment labels, not universal mechanism proof.

---

## 11. Part C — bounded persistence-budget sensitivity

Run only if layer0 up_proj natural D3 shows a material DRAM or timing benefit under `PERSIST_L0_UP`.

Target:
- layer0 up_proj qweight;
- natural D3.

Budgets:

- 8 MiB
- 16 MiB
- 24 MiB
- 32 MiB
- full qweight budget

For budgets smaller than the qweight window:

- keep access-policy window = full qweight tensor;
- set `hitRatio = min(1.0, budget_bytes / qweight_bytes)`;
- set persisting-L2 limit to the tested budget.

Native:
- 7 fresh processes per budget.

NCU:
- D3 only;
- same three traffic metrics;
- one profile per budget.

Report:
- requested/actual budget;
- hitRatio;
- target timing;
- target DRAM;
- first tested budget with material benefit;
- no exact hardware threshold claim.

Do not run this sweep if the full-qweight condition has no material effect.

---

## 12. Part D — mechanism-requirement extraction

This part is documentation/analysis only.

If target persistence is materially beneficial under natural full-model reuse, derive a minimum abstract requirement set:

- **object class**: compressed weight region / qweight-like data;
- **granularity**: line-level protection within a software- or hardware-identified address interval;
- **lifetime**: across the inter-token reuse interval;
- **budget**: bounded by measured budget sensitivity, not assumed from nominal state size;
- **selectivity**: cannot protect all model weights simultaneously;
- **replacement interaction**: protected target lines should resist interference from unrelated model weights;
- **fallback**: non-target data follows normal policy;
- **identity source candidates**:
  - software metadata/range hint;
  - static load/instruction signature;
  - learned/runtime reuse classification.

Do not choose or implement one classifier/replacement algorithm yet.

If no material natural benefit is observed, record:

`TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`

and do not proceed to a cache mechanism.

---

## 13. Optional end-to-end observation

Always record decode-step latency.

But because only one layer/role is protected at a time:

- do not require end-to-end speedup;
- do not extrapolate linearly to all layers;
- do not claim model-level benefit from a single protected module.

---

## 14. Required 109 review pack

`docs/vm_tlb/review_packs/C16_E1_L2_PERSISTENCE_INTERVENTION_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `CUDA_PERSISTENCE_CAPABILITY.json`
- `QWEIGHT_REGION_CENSUS.tsv`
- `POLICY_IMPLEMENTATION_CONTRACT.json`
- `ISOLATED_QUALIFICATION_TIMING.tsv`
- `ISOLATED_QUALIFICATION_NCU.tsv`
- `ISOLATED_QUALIFICATION_ANALYSIS.json`
- `NATURAL_POLICY_CONDITIONS.json`
- `NATURAL_POLICY_NATIVE_TIMING.tsv`
- `NATURAL_POLICY_NCU_INDEX.tsv`
- `NATURAL_POLICY_ANALYSIS.json`
- `BUDGET_SENSITIVITY_TIMING.tsv`
- `BUDGET_SENSITIVITY_NCU.tsv`
- `BUDGET_SENSITIVITY_ANALYSIS.json`
- `MECHANISM_REQUIREMENTS.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Preserve raw BASE/SESSION/PROFILE logs and policy receipts for all NCU points.

Update the living low-bit/shape scientific log.

---

## 15. Independent 174-new consumer

Parallel consumer should:

- audit CUDA policy contract;
- freeze exact condition matrix/materiality rules;
- independently parse policy receipts;
- independently consume native raw timing;
- independently consume raw NCU BASE+SESSION+PROFILE;
- verify same token/occurrence identity across conditions;
- independently compute target/setaside/unrelated effects;
- independently recompute budget sensitivity;
- independently derive whether mechanism preconditions are met;
- fetch producer once after prep.

No GPU work.

---

## 16. Final boundary

This Goal may authorize only one of:

- `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`
- `TARGETED_PERSISTENCE_TRAFFIC_ONLY`
- `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`
- `CUDA_PERSISTENCE_POLICY_UNQUALIFIED`

It must not automatically start:

- NVBit;
- full address trace;
- Accel-Sim mechanism implementation;
- cache/TLB mechanism simulation.

Those require the producer + independent consumer closure and ChatGPT review.
