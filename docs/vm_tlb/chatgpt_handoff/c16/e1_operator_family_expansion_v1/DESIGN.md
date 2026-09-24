# C16 E1 Operator-Family Expansion and Residual Decomposition Design V1

## 1. Purpose

The up_proj-only coverage curve is positive but sub-2%, while all FFN projections occupy ~47.4% of stable decode.

At N28:
- selected up_proj share ~16.6%;
- summed local up_proj saving ~0.567 ms;
- observed decode saving ~0.123 ms;
- realization ~0.216.

The missing ~0.44 ms is not yet attributed.

This stage answers two questions before simulator implementation:

1. Where does the realization loss go when broad up_proj persistence is enabled?
2. Under the same fixed total persisting-L2 budget, does expanding protection from one FFN role to multiple FFN roles produce system-level decode benefit?

No simulator is run in this stage.

---

## 2. Frozen hardware/runtime authority

Model:
`Qwen/Qwen2.5-7B-Instruct`

Deployment:
accepted AWQ full-model path.

Input:
accepted S2_TEXT 2048-token prefix.

Decode:
four deterministic greedy steps.

Expected tokens:
`[23578, 11, 323, 3950]`

GPU:
RTX4080.

Requested persisting-L2 set-aside:
`33,947,648 B`

Expected runtime query-back:
`37,748,736 B`

All conditions must preserve:
- model/token/backend identity;
- exact qweight intervals;
- requested/actual set-aside;
- no in-run persistence reset.

---

## 3. FFN module universe

The producer has already established:

- 28 layers;
- three AWQ qweight-backed roles per layer:
  - gate_proj
  - up_proj
  - down_proj;
- 84 total FFN projection modules;
- each qweight region is exact/contiguous and independently addressable.

This stage times all 84 FFN projections in every condition.

For each D0-D3 occurrence preserve:
- layer;
- role;
- input/output SHA;
- module class/backend;
- qweight interval;
- CUDA-event timing.

No inner-loop synchronize.

---

## 4. Natural policy update order

Do not impose an artificial role order.

First run one no-policy authority probe and record the natural FFN module call sequence for:
- PREFILL;
- D0;
- D1;
- D2;
- D3.

Require the same module-call order in all fresh processes.

For every policy condition:
- apply the policy update immediately before the selected module's natural invocation;
- do not reorder modules;
- matched CONTROL and FAIR use the exact same selected-module update locations.

The call-order receipt is first-class authority.

---

## 5. Condition matrix

Every condition uses one fixed total set-aside.

### Role-only, all 28 layers

- CONTROL_GATE28
- FAIR_GATE28

- CONTROL_UP28
- FAIR_UP28

- CONTROL_DOWN28
- FAIR_DOWN28

### Pairwise role families, all 28 layers

- CONTROL_GU56
- FAIR_GU56

- CONTROL_GD56
- FAIR_GD56

- CONTROL_UD56
- FAIR_UD56

### All FFN projections

- CONTROL_GUD84
- FAIR_GUD84

Total:
14 conditions.

Every condition:
- 7 fresh processes;
- all 84 FFN projections timed;
- D0-D3 decode-step timing;
- complete ordered policy receipt;
- CPU policy-update overhead.

---

## 6. Selected-module policy

For a condition with K selected modules:

### CONTROL

Immediately before each selected module call:

- exact selected module qweight window;
- hitRatio = `1/K`;
- hitProp = NORMAL;
- missProp = NORMAL;
- target_persisting = false.

### FAIR

Same exact update point/window:

- hitRatio = `1/K`;
- hitProp = PERSISTING;
- missProp = STREAMING;
- target_persisting = true.

No policy update is performed for unselected modules.

Reset:
- before the whole condition;
- after the whole condition;
- never between selected module calls.

CUDA hitRatio is a policy hint, not a deterministic exact protected-line fraction.

---

## 7. Why role-specific matched controls are separate

CONTROL_GATE28, CONTROL_UP28, CONTROL_DOWN28, and the pair/all-role controls are not interchangeable.

Each control must match its FAIR condition in:
- selected module addresses;
- update count;
- update location;
- hitRatio field;
- host API sequence.

This avoids attributing address-window/API-structure differences to persistence.

---

## 8. Direct benefit and residual decomposition

For every condition and stable D1-D3, compute run-aligned:

### SELECTED_SHARE

`sum CONTROL selected FFN timing / CONTROL decode-step timing`

### DIRECT_SELECTED_SAVING

`sum(CONTROL selected module timing - FAIR selected module timing)`

### UNSELECTED_FFN_SAVING

`sum(CONTROL unselected FFN timing - FAIR unselected FFN timing)`

### TOTAL_FFN_SAVING

`DIRECT_SELECTED_SAVING + UNSELECTED_FFN_SAVING`

### OBSERVED_DECODE_SAVING

`CONTROL decode-step timing - FAIR decode-step timing`

### OUTSIDE_FFN_RESIDUAL

`OBSERVED_DECODE_SAVING - TOTAL_FFN_SAVING`

Interpretation:
- positive residual: improvement exists outside measured FFN projection timing or via overlap/accounting;
- negative residual: measured FFN savings are partially offset outside the FFN projection accounting.

Do not automatically call the negative residual cache collateral slowdown.

### SELECTED_REALIZATION

`OBSERVED_DECODE_SAVING / DIRECT_SELECTED_SAVING`

### FFN_REALIZATION

`OBSERVED_DECODE_SAVING / TOTAL_FFN_SAVING`

when denominators are positive.

Do not clamp.

---

## 9. Role decomposition

For every CONTROL/FAIR pair report stable D1-D3 run-aligned:

- gate_proj aggregate saving;
- up_proj aggregate saving;
- down_proj aggregate saving;
- total FFN saving;
- outside-FFN residual;
- whole-decode saving.

This directly tests whether protecting one role speeds or slows the other FFN roles.

Example questions:

- Does FAIR_UP28 make gate/down slower?
- Does FAIR_GATE28 help or hurt up/down?
- Does protecting gate+up reduce the residual compared with up-only?
- Does all-FFN persistence convert more direct local saving into full-decode saving?

---

## 10. Local materiality

For each selected module at D3:

`MATERIAL_LOCAL`

if:
- FAIR timing >=5% lower than matched CONTROL;
- effect > combined timing dispersion.

For each condition report:
- material selected count;
- material selected fraction;
- benefit distribution by role/layer.

Do not require every selected module to pass.

---

## 11. Whole-decode materiality

For each run:
`stable_decode = mean(D1,D2,D3)`

FAIR is compared only to its matched CONTROL.

A system point is:

`MATERIAL_SYSTEM`

if:
- whole-decode benefit >=2%;
- and benefit > combined dispersion.

The 2% threshold is retained from the previous coverage design.

Also report positive-beyond-dispersion effects below 2%.

---

## 12. Host policy-overhead accounting

For every condition record:

- per-update CPU duration;
- total policy API duration per run;
- CONTROL-vs-FAIR overhead difference.

Do not automatically subtract host API time from GPU decode timing.

Instead report both and preserve whether host-side difference is comparable to the observed decode saving.

This is a diagnostic, not a correction formula.

---

## 13. Representative NCU matrix

Re-query installed NCU metric availability.

Use accepted base metrics:
- L1/TEX bytes;
- L2 bytes;
- DRAM bytes.

Use critical-path categories where still available:
- kernel duration;
- L2 read hit sectors;
- L2 read miss sectors;
- DRAM read bytes;
- long-scoreboard stall;
- LSU utilization;
- active warps.

Profile D3 only.

### Gate representative L0

- CONTROL_GATE28
- FAIR_GATE28
- CONTROL_GUD84
- FAIR_GUD84

### Up representative L0

- CONTROL_UP28
- FAIR_UP28
- CONTROL_GUD84
- FAIR_GUD84

### Down representative L0

- CONTROL_DOWN28
- FAIR_DOWN28
- CONTROL_GUD84
- FAIR_GUD84

Maximum:
12 profiles.

Application replay + cache-control none.

Preserve full natural policy history before selected D3 occurrence.

Non-additive percentages remain per-kernel.

---

## 14. Conditional FULLHINT all-FFN control

Because GUD84 has K=84, a bounded over-subscribed-intent control is preauthorized if:

- FAIR_GUD84 selected material fraction >=0.50;
- and FAIR_GUD84 whole-decode benefit <2%.

Then run:

- CONTROL_FULL_GUD84
- FULLHINT_GUD84

Both:
- same 84-module update locations;
- fixed requested/actual set-aside;
- all selected windows full exact qweight intervals;
- hitRatio=1.0.

CONTROL:
NORMAL/NORMAL.

FULLHINT:
PERSISTING/STREAMING.

Native:
7 fresh processes each.

Additional NCU:
only if FULLHINT_GUD84 changes whole-decode benefit by >=0.5 percentage points versus FAIR_GUD84.

If triggered, profile L0 gate/up/down D3 CONTROL_FULL_GUD84 vs FULLHINT_GUD84.

Interpretation:
FULLHINT is over-subscribed policy intent, not evidence that all 84 qweights fit.

---

## 15. Frozen stage outcomes

### OPERATOR_FAMILY_SYSTEM_RELEVANT

At least one predeclared FAIR role/pair/all-family condition:
- whole-decode benefit >=2%;
- benefit > combined dispersion.

### OPERATOR_FAMILY_COLLATERAL_LIMITED

No condition reaches system relevance, but:
- FAIR_GUD84 direct selected saving corresponds to >=2% of CONTROL_GUD84 decode time;
- at least 50% of GUD84 selected modules are MATERIAL_LOCAL;
- OUTSIDE_FFN_RESIDUAL median is negative.

This label means local FFN savings are large enough in principle, but the full-decode result is offset outside measured FFN timing.

It does not establish the cause of the residual.

### OPERATOR_FAMILY_POSITIVE_BUT_SUBTHRESHOLD

No system-relevant point and no COLLATERAL_LIMITED classification, but at least one condition is positive beyond dispersion.

### OPERATOR_FAMILY_NOT_SUPPORTED

No predeclared condition has positive whole-decode benefit beyond dispersion.

### POLICY_FAMILY_SCALING_UNQUALIFIED

Policy/runtime/semantic identity cannot be qualified.

Precedence:

1. POLICY_FAMILY_SCALING_UNQUALIFIED
2. OPERATOR_FAMILY_SYSTEM_RELEVANT
3. OPERATOR_FAMILY_COLLATERAL_LIMITED
4. OPERATOR_FAMILY_POSITIVE_BUT_SUBTHRESHOLD
5. OPERATOR_FAMILY_NOT_SUPPORTED

No simulator implementation is auto-authorized by the producer.

---

## 16. 109 review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_OPERATOR_FAMILY_EXPANSION_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `NATURAL_FFN_CALL_ORDER.json`
- `OPERATOR_FAMILY_POLICY_CONTRACT.json`
- `OPERATOR_FAMILY_NATIVE_TIMING.tsv`
- `OPERATOR_FAMILY_DECODE_TIMING.tsv`
- `OPERATOR_FAMILY_POLICY_OVERHEAD.tsv`
- `OPERATOR_FAMILY_RUN_ALIGNED_ACCOUNTING.tsv`
- `ROLE_ONLY_ANALYSIS.json`
- `PAIRWISE_ANALYSIS.json`
- `ALL_FFN_ANALYSIS.json`
- `RESIDUAL_DECOMPOSITION.json`
- `OPERATOR_FAMILY_NCU_INDEX.tsv`
- `OPERATOR_FAMILY_CRITICAL_PATH.json`
- `FULLHINT_GUD84_TRIGGER.json`
- `FULLHINT_GUD84_ANALYSIS.json`
- `STAGE_DECISION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Preserve all raw native/NCU/policy evidence.

Update scientific log.

---

## 17. 174-new parallel role

174-new should:

1. independently close the completed coverage producer from raw evidence;
2. preserve coverage producer label separately from independent consumer label;
3. explicitly audit the N28 realization residual;
4. freeze the operator-family consumer before operator-family producer data;
5. implement raw consumers for:
   - natural call order;
   - all-84 FFN timing;
   - policy histories;
   - direct/unselected/residual decomposition;
   - host-overhead accounting;
   - representative NCU;
   - FULLHINT GUD84;
6. fetch operator-family producer once after prep and consume if complete;
7. otherwise stop READY.

No simulator run.

---

## 18. Next-step review after independent closure

ChatGPT will choose among:

- `AUTHORIZE_BOUNDED_TRACE_AND_FIRST_SIMULATOR_MECHANISM`
- `REVISE_MECHANISM_TO_ADDRESS_COLLATERAL_RESIDUAL`
- `EXTEND_BEYOND_FFN_BEFORE_SIMULATOR`
- `STOP_RESIDENCY_MECHANISM_SYSTEM_CASE_WEAK`
- `REVIEW_REQUIRED`

No producer/consumer auto-authorizes simulator code mutation.
