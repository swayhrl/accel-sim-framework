# CODEX_NEXT_STAGE

Status: **ACTIVE — TRACK C + TRACK D**

Coordination stage:

```text
AWMA_STORAGE_GOVERNANCE_AND_GPU_CAPTURE_SIDELANE_V1
```

Previous tracks:

```text
Track A — 174-new Q05 translation timeline closure
COMPLETE / report received

Track B — 109 target selection
COMPLETE / ACCEPTED
```

Current active tracks:

```text
Track C — 109 producer-side storage governance + bounded GPU capture side lane
Track D — 174-new independent node164 storage consumer audit
```

## Coordination branch

`hrl/awma-storage-governance-gpu-sidelane-handoff-v1`

All Codex instances must read:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/STORAGE_GOVERNANCE_POLICY_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute only the active node-specific specification.

---

## Track C — node109 — ACTIVE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md`

Parent authority:

```text
hrl/awma-kernel-target-selection-109-v1
e90fd76d3704df4a367bb04de09aee42d0cab803
```

Strict sequence:

```text
Phase A
storage governance + producer-side node164 data-plane qualification

required gate:
AWMA_164_DATA_PLANE_QUALIFIED_V1

then only if PASS:

Phase B
bounded simulator-native producer capture side lane
```

Authorized candidates only:

```text
PREFILL_GEMM_PRIMARY_1
DECODE_GEMV_PRIMARY_1
DECODE_FLASH_PRIMARY_1
DECODE_FLASH_PRIMARY_2
```

Scientific identity must re-close on frozen workload + phase + exact function + grid/block + deterministic occurrence (+ decode step where applicable). Reference global launch indexes are navigation aids only.

Track C may produce producer-qualified durable bundles on node164. It may not create SIM_INPUT IDs or run simulation.

Expected completion:

`AWMA_STORAGE_GOVERNANCE_GPU_SIDELANE_V1_COMPLETE_WITH_SCOPE`

---

## Track D — 174-new — ACTIVE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_STORAGE_CONSUMER_AUDIT_V1.md`

Purpose:

independently audit node164 as the durable consumer/simulator-side authority rather than trusting only producer-side publication state.

This is read-mostly. It must not modify simulator science or duplicate GPU capture.

Required areas:

- node164 mount/capacity/permissions from 174-new;
- durable inventory of accepted Q05 trace, natural/full simulation raw, translation-timeline raw and S2 census data;
- independent consumer rehash/receipt verification;
- producer canary/ACK read-back verification when Track C Phase A becomes available;
- deterministic catalog consumption from 174-new;
- orphan partial/local-only/duplicate-authority/cleanup-candidate detection;
- no deletion or mass move.

Expected completion:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_COMPLETE_WITH_SCOPE`

If producer Phase A is not yet complete, Track D must finish all independent work and may close as:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_WAITING_FOR_PRODUCER_CANARY`

Do not invent missing producer receipts.

---

## Storage authority

Durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Roles:

```text
109 = producer / short-lived staging
174-new = simulator / analysis / independent durable consumer
164 = durable large-data authority
```

Existing accepted durable paths are provenance and must not be mass-moved.

New producer captures must pass partial/resume/size/SHA/admission/ACK closure before durable status.

No accepted scientific data may be deleted in this stage.

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

Current accepted Q05 SIM_INPUT/baseline/run/evidence identities remain read-only.

---

## Explicitly forbidden scope

Neither active track may automatically start:

- TLB/PTW/cache mechanisms;
- L2-TLB latency/PTW/walker/capacity/page-size sweeps;
- Segment;
- NCU campaigns;
- C16WARP1 campaigns;
- Qwen3/DeepSeek campaigns;
- secondary long-duration Decode GEMV capture;
- SIM_INPUT admission or Accel-Sim replay of new Track C bundles;
- deletion or reorganization of accepted node164 evidence.

## Execution policy

Routine engineering/storage/index/Git problems are solve-and-continue.

Stop for review only for:

- scientific identity conflict;
- provenance contradiction;
- destructive storage risk;
- inability to prove destination integrity;
- need to weaken trace semantics;
- collision with another formal GPU campaign.

Each active track independently:

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

After Track C and Track D complete, return both reports to ChatGPT. Do not auto-start the next simulation or mechanism stage.
