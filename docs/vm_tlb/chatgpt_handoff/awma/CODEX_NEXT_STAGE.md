# CODEX_NEXT_STAGE

Status: **ACTIVE — TRACK A + TRACK C**

Coordination stage:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE
+
AWMA_STORAGE_GOVERNANCE_AND_GPU_CAPTURE_SIDELANE_V1
```

The previous node109 target-selection Track B is COMPLETE / ACCEPTED. Its output is now the authority for the bounded Track C capture list.

## Coordination branch

```text
hrl/awma-storage-governance-gpu-sidelane-handoff-v1
```

Codex must fetch this branch and read:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Node109 must additionally read:

```text
docs/vm_tlb/chatgpt_handoff/awma/STORAGE_GOVERNANCE_POLICY_V1.md
```

Then execute only its ACTIVE node-specific specification.

---

## Track A — 174-new — ACTIVE / unchanged

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_174NEW_Q05_TRANSLATION_TIMELINE_CLOSURE_V1.md
```

Parent:

```text
hrl/awma-q05-full-translation-174new-v1
6415d3f1
```

Expected completion:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE
```

Track A remains diagnostic-only and pre-mechanism.

Track C must not modify Track A's worktree or simulator state.

---

## Track B — 109 target selection — COMPLETE / ACCEPTED

Accepted result:

```text
branch = hrl/awma-kernel-target-selection-109-v1
HEAD   = e90fd76d3704df4a367bb04de09aee42d0cab803
status = AWMA_KERNEL_TARGET_SELECTION_V1_COMPLETE_WITH_SCOPE
review = PASS_WITHIN_SCOPE
```

Track B must not be restarted.

Accepted candidates are defined by its `CANDIDATE_STATUS.json` and remain immutable selection anchors.

---

## Track C — 109 storage governance + GPU side lane — ACTIVE

Execute:

```text
docs/vm_tlb/chatgpt_handoff/awma/
CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md
```

Recommended execution branch:

```text
hrl/awma-storage-governance-capture-sidelane-109-v1
```

Create from accepted node109 Track B commit:

```text
e90fd76d3704df4a367bb04de09aee42d0cab803
```

Track C is sequential:

```text
Phase A
storage governance + node164 data-plane qualification

required gate:
AWMA_164_DATA_PLANE_QUALIFIED_V1

then only if PASS:

Phase B
bounded simulator-native producer captures
```

Authorized capture candidates only:

```text
PREFILL_GEMM_PRIMARY_1
DECODE_GEMV_PRIMARY_1
DECODE_FLASH_PRIMARY_1
DECODE_FLASH_PRIMARY_2
```

The global launch indexes recorded by census are navigation aids only. Each capture must re-close frozen workload + phase + exact function + grid/block + deterministic occurrence (+ decode step where applicable).

Track C may publish producer-qualified durable bundles to node164, but may not create SIM_INPUT IDs or run simulation.

Expected completion:

```text
AWMA_STORAGE_GOVERNANCE_GPU_SIDELANE_V1_COMPLETE_WITH_SCOPE
```

---

## Durable storage rule

Large AWMA data belongs on node164:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/
```

Roles:

```text
109 = producer / temporary staging
174-new = simulator / analysis
164 = durable data authority
```

Existing accepted paths are provenance and must not be mass-moved.

New large producer captures must use partial/resume/hash/admission/ACK closure before being considered durable.

No accepted scientific data may be deleted in Track C.

---

## Shared frozen workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
input      = frozen TEXT binding
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

Current accepted Q05 simulation identities and baseline remain read-only.

---

## Shared execution policy

Routine engineering problems are solve-and-continue.

Stop for scientific review if continuing would require:

- changing frozen workload identity;
- guessing a target identity;
- changing Q05/SIM_INPUT scientific identity;
- modifying TLB/PTW timing/functionality outside Track A's timing-neutral diagnostics;
- weakening simulator-native trace semantics;
- fabricating missing address/width/immediate fields;
- overwriting accepted durable data;
- interrupting another formal GPU campaign.

---

## Explicitly forbidden scope

Neither active track may automatically start:

- L2-TLB latency sweep;
- PTW fixed-latency experiment;
- walker/count/capacity/page-size sweeps;
- Segment;
- new TLB/cache mechanism;
- NCU campaign;
- C16WARP1 campaign;
- Qwen3/DeepSeek campaign;
- secondary long-duration Decode GEMV capture;
- SIM_INPUT admission or Accel-Sim replay of Track C captures.

---

## Completion

Each active track must independently:

```text
finish scope
-> review pack
-> report
-> hashes
-> commit
-> push
-> remote verify
-> clean worktree
-> STOP
```

After both Track A and Track C complete, return both reports to ChatGPT for the next scientific decision.
