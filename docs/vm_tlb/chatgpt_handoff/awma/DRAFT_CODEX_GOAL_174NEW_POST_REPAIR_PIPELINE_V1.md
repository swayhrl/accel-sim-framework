# DRAFT — CODEX GOAL 174-new Post-Repair 20h Pipeline V1

Date: 2026-09-19

Status: `PRE_REPAIR_DRAFT_NOT_EXECUTABLE`

Node: 174-new / simulator-analysis node

Execution mode: GOAL MODE, solve-and-continue.

This draft cannot be executed before ChatGPT independently reviews the current VM per-access
coverage repair report and publishes a final coordination commit.

## 0. Mission

After the repair review, use only the explicitly approved repaired runtime to:

1. close the minimum translation-baseline requalification needed to reinterpret Q05;
2. avoid rerunning obsolete historical sweeps;
3. use existing accepted evidence to build a cross-family comparison;
4. conditionally screen one non-Attention family under repaired R0/I0 semantics if the
   scientific and consumer gates are fully closed.

No new architecture mechanism is authorized.

## 1. Final-version bindings

The final coordination commit MUST replace:

`<POST_REPAIR_DECISION>`
`<POST_REPAIR_EXECUTION_BRANCH>`
`<POST_REPAIR_EXECUTION_SHA>`
`<POST_REPAIR_BINARY_SHA>`
`<POST_REPAIR_REVIEW_PACK_SHA>`
`<POST_REPAIR_REQUALIFICATION_POLICY>`
`<FINAL_174_EXECUTION_PARENT>`
`<FINAL_174_EXECUTION_BRANCH>`
`<CAMPAIGN_START_UTC>`
`<CAMPAIGN_DEADLINE_UTC>`

The final file MUST also enumerate which already-executed repair qualification runs are accepted
for direct reuse.

## 2. Allowed post-repair decision cases

### Case A — Repair qualified and baseline requalification authorized

Possible decision anchor:

`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED`

This label alone is not enough. ChatGPT final handoff must explicitly approve the runtime as the
candidate requalification runtime and bind exact SHA/binary.

Then execute Stage 174-M0.

### Case B — Defect confirmed, repair not yet qualified

Do not run requalification or opportunity simulations.

Allowed work:

- source/evidence analysis that does not rely on repaired quantitative timing;
- review-pack completion explicitly authorized by the final handoff.

Otherwise STOP.

### Case C — Undercoverage hypothesis not reproduced

Do not execute the candidate repaired-baseline plan.

The final handoff must provide a different analysis contract.

### Case D — Repair materially changes scientific interpretation but final baseline decision is
not approved

STOP for scientific review.

No autonomous promotion is allowed.

## 3. Stage 174-M0 — Minimal repaired Q05 requalification

The final handoff will mark each candidate identity as:

`REUSE_ACCEPTED_REPAIR_RUN`
`RUN_REQUIRED`
`DISABLED`

Candidate identities:

1. `FORMAL_ISOLATED_REPAIRED_R0`
2. `FORMAL_ISOLATED_REPAIRED_I0`
3. `P34_REPAIRED_R0`
4. `P34_REPAIRED_Q05_ONLY_I0`
5. `P8_REPAIRED_R0`
6. bounded translation/timeline sanity derived from these runs where possible

Do not rerun an identity already accepted with exact matching:

- source SHA;
- binary SHA;
- config;
- input/context bundle;
- target boundary;
- VM semantic contract;
- telemetry contract.

### 3.1 R0 contract

Every VM-eligible access follows the accepted repaired per-access translation gate.

Required invariants must remain closed:

- zero untranslated downstream admissions;
- zero post-ready retranslation attempts;
- exact eligible/admission/translated conservation per accepted scope.

### 3.2 I0 contract

I0 remains an ideal identity-translation diagnostic.

For Q05-only contextual I0:

- every predecessor runs repaired natural R0;
- only Q05 target accesses use the approved I0 semantics;
- I0 applies per access with no legacy undercoverage;
- SimVA → same SimPA identity is preserved;
- no hidden predecessor idealization.

If exact per-access target-I0 cannot be implemented under the repaired contract, mark:

`REPAIRED_TARGET_I0_DEFERRED`

Do not approximate.

### 3.3 Context contract

Formal isolated / P8 / P34 comparisons must use accepted same-source target identity and accepted
contiguous context members.

Do not substitute the historical standalone 885681-cycle isolated run for a same-source repaired
formal isolated run.

### 3.4 Required metrics

For every R0/I0 run that is actually executed or reused:

- full target cycles;
- active-thread instructions;
- CTA/warp completion;
- GLOBAL/LOCAL VM-eligible accesses;
- translated coverage;
- L1/L2 TLB accesses/hits/misses;
- MSHR alloc/merge/HWM/full;
- walk start/complete;
- PWC/PTE;
- requester-latency components;
- L2 data accesses/misses;
- DRAM counters;
- coverage invariants.

Do not use REQUEST invocation counts as unique memory requests.

### 3.5 M0 decisions

Produce:

`REPAIRED_Q05_REQUALIFICATION_MATRIX.tsv`

and compute at minimum:

- repaired isolated R0 vs repaired isolated I0 sensitivity;
- repaired P34 R0 vs repaired P34 Q05-only I0 sensitivity, if I0 qualified;
- isolated vs P8 vs P34 natural behavior;
- repaired-vs-legacy deltas where the metric is semantically comparable.

Classify old translation claims:

`RETAINED_WITH_NEW_VALUES`
`QUALITATIVELY_RETAINED`
`MATERIALLY_REVISED`
`RETIRED`
`NOT_YET_REQUALIFIED`

Do not preserve an old numeric conclusion merely because its direction remains the same.

## 4. Stage 174-O1 — Existing cross-family evidence analysis

Class: CPU-only opportunistic analysis.

This stage uses accepted existing evidence to decide which family adds behavior not already
represented by Q05.

Candidate families:

- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1;
- Decode Flash Primary-2 tiny control.

### 4.1 Normalize evidence units

For each family, report only metrics whose units are genuinely comparable:

- dynamic instruction / record counts;
- memory-instruction counts;
- active-lane address events under the same parser definition;
- opcode/memory-path composition;
- page footprint under the same page-size accounting;
- cache-line footprint if already accepted;
- native frequency/time share from accepted census when identity joins exactly;
- current simulator qualification status.

Do not force-join offline VPN counts to simulator translation keys.

### 4.2 Required outputs

`CROSS_FAMILY_EXISTING_EVIDENCE_MATRIX.tsv`

`CROSS_FAMILY_EVIDENCE_GAPS.md`

`NEXT_FAMILY_SELECTION_RATIONALE.md`

The rationale must answer:

- what behavior a family adds;
- which evidence level is available;
- which evidence is missing;
- what a repaired simulator run would discriminate.

No mechanism recommendation is allowed.

## 5. Stage 174-C1 — Conditional first non-Attention repaired R0/I0 screen

This stage is disabled unless the final handoff explicitly enables it.

Entry gates:

1. repaired runtime / binary formally accepted for requalification;
2. 174-M0 accepted;
3. selected target consumer input is qualified under the current simulator contract;
4. complete target can naturally finish;
5. exact R0 and I0 semantics can be applied per access;
6. enough time remains for paired execution plus finalization.

Priority target:

1. Prefill GEMM Primary;
2. Decode GEMV Primary only if Prefill GEMM cannot meet qualification gates.

At most one family.

### 5.1 Scientific question

Does repaired translation sensitivity observed in Q05 also appear in a non-Attention family?

This is a screening experiment, not a mechanism evaluation.

### 5.2 Pairing

Run/reuse exactly:

`<TARGET>_REPAIRED_R0`

`<TARGET>_REPAIRED_I0`

If no same-source predecessor context exists, label the result:

`ISOLATED_SCREEN_ONLY`

Do not compare it directly with P34 as if context were matched.

### 5.3 Required outputs

- complete cycles;
- instruction progress/completion;
- repaired coverage invariants;
- full translation telemetry;
- L2/DRAM context;
- exact input/source/binary/config identities;
- R0/I0 sensitivity.

Do not launch capacity/port/lookup/page-size/PTW/PWC sweeps.

## 6. Solve-and-continue policy

Engineering issue:

- solve safely;
- record change;
- rerun local test;
- continue.

Scientific issue:

- freeze affected task;
- preserve evidence;
- mark `STOP_SCIENTIFIC`;
- continue only independent authorized analysis.

Whole-goal STOP if repaired-source authority, binary identity, context/input authority, or
shared telemetry contract becomes ambiguous.

## 7. Time policy

Final handoff sets campaign start/deadline.

No new simulator scientific target in final 2 hours.

During final reserve:

- finish only safely closable running work;
- hash/transfer/admit;
- generate reports/review pack;
- commit/push/remote verify;
- clean worktree;
- STOP.

## 8. Durable outputs

Large logs:

`/root/share/mnt164/huangrulin/<FINAL_174_CAMPAIGN_ROOT>/`

Review pack should include at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `PIPELINE_STATE.json`
- `POST_REPAIR_AUTHORITY.md`
- `REPAIRED_Q05_REQUALIFICATION_MATRIX.tsv`
- `LEGACY_CLAIM_REQUALIFICATION.md`
- `COVERAGE_INVARIANTS.tsv`
- `RUN_RECEIPTS.json`
- `RAW_DATA_INDEX.tsv`
- cross-family analysis files if executed
- non-Attention screen files if executed
- `SHA256SUMS`

Final report must enumerate reused runs separately from newly executed runs.

Then commit → push → remote verify → clean worktree → STOP.

## 9. Forbidden

- no new architecture mechanism;
- no TLB capacity/port sweep;
- no lookup-latency sweep;
- no PTW/PWC optimization;
- no page-size/segmentation/prefetch/speculation;
- no automatic full historical replay;
- no silent promotion of repaired runtime;
- no rewriting accepted legacy packs;
- no treating native RTX4080 reconnaissance as lookup-latency calibration.
