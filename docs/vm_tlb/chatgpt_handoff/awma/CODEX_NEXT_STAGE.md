# CODEX_NEXT_STAGE

Status: **ACTIVE**

Date: 2026-09-20

Stage:

`AWMA_MAINLINE_RESET_AND_CROSS_TARGET_VALIDITY_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

## 1. Read first

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/EXECUTION_PRIORITY_POLICY_V2.md
docs/vm_tlb/chatgpt_handoff/awma/CANDIDATE_SIDE_LANES.md
docs/vm_tlb/chatgpt_handoff/awma/CROSSVIEW_JOIN_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

## 2. P0 prerequisites — must close before new mainline science

### node109

The currently running MoE causal-closure campaign is a candidate side lane.

Execute:

`CODEX_PAUSE_109_MOE_CAUSAL_FOR_MAINLINE.md`

Required result:

`AWMA_109_MOE_CAUSAL_CLOSURE_PAUSED_FOR_MAINLINE`

Do not discard completed C2 evidence.

Do not continue the side lane merely to use its 20h allocation.

### 174-new

Close the V4 remote-publication blocker.

Execute:

`CODEX_CLOSE_174_V4_REMOTE_PUBLICATION.md`

Required result:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED`

No simulation rerun.

## 3. P1/P2 dual-track mainline

Only after both P0 prerequisites close.

### Track A — 174-new / Simulation Evidence Plane

Execute:

`CODEX_NEXT_STAGE_174_CROSS_TARGET_HITPATH_VALIDITY_V1.md`

Target set:

```text
T0 Q05_PREFILL_ATTN_FLASH
T1 PREFILL_GEMM_PRIMARY_OCC0
T2 DECODE_GEMV_PRIMARY_STEP16
```

Objective:

test repaired hit-path model validity across Attention / Prefill GEMM / Decode GEMV.

No mechanism design.

### Track B — 109 / Native Evidence Plane

Execute:

`CODEX_NEXT_STAGE_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1.md`

Same exact target set.

Objective:

close native timing/resource/footprint evidence for later Cross-view.

No MoE/AWQ continuation.

## 4. Shared workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

## 5. Mainline scientific objective

Determine whether the repaired simulator's large translation hit-path sensitivity:

- persists across representative kernel classes;
- is dominated by Attention;
- is target-dependent;
- or indicates a simulator hit-path semantic/calibration issue.

## 6. Cross-view rule

Both tracks must follow:

`CROSSVIEW_JOIN_CONTRACT_V1.md`

Native and Simulation evidence remain separate classes.

No direct equivalence between hardware timing/counters and simulator cycles/lookup latencies is allowed without an explicit aligned definition.

## 7. Candidate side lanes

Frozen:

- Q30 MoE routing-skew;
- MoE causal-closure partial campaign after pause;
- raw/AWQ implementation-policy work.

See:

`CANDIDATE_SIDE_LANES.md`

They may not consume mainline resources unless explicitly reactivated.

## 8. Engineering policy

Routine engineering issues are solve-and-continue.

Examples:

- paths;
- parsers;
- build;
- selectors;
- NCU metric discovery;
- trace admission;
- receipts;
- Git publication.

Scientific review is required for:

- target/model/input identity changes;
- simulator semantic changes;
- evidence-class changes;
- mechanism authorization.

## 9. 174 remote publication

Every 174 Goal must follow:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

A local-only result is not complete.

## 10. Global STOP boundary

After Track A and Track B both complete:

- stop;
- return both reports/review packs to ChatGPT;
- do not automatically launch Cross-view conclusions or architecture mechanisms.

ChatGPT will issue the next scientific decision.
