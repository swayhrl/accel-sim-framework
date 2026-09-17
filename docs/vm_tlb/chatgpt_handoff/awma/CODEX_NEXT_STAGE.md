# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — M1 + M2**

Stage:

`AWMA_Q05_CONTEXT_WARMUP_SENSITIVITY_V1`

## Coordination branch

`hrl/awma-q05-context-warmup-handoff-v1`

All Codex instances must fetch this branch and read, in order:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTEXT_WARMUP_EXPERIMENT_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute only the node-specific ACTIVE mainline specification.

---

## Mainline M1 — node109 / RTX4080 — ACTIVE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_109_Q05_NATIVE_CONTEXT_CHARACTERIZATION_V1.md`

Recommended execution parent/branch:

```text
parent = c17df93f9c44aa35d2942ae696bc2bd2a30b3643
branch = hrl/awma-q05-native-context-109-v1
```

Objective:

- recover exact native predecessor launch sequence before Q05;
- observe predecessor/Q05 page sets in one exact execution context;
- quantify page-overlap opportunity and temporal distance;
- measure normal-context Q05 timing stability;
- optionally measure data-cache-sensitive NCU differences with explicit caveats;
- recommend bounded continuous predecessor prefixes for the next simulation stage.

This track owns the RTX4080 while ACTIVE.

Expected completion:

`AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1_COMPLETE_WITH_SCOPE`

---

## Mainline M2 — node174-new — ACTIVE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_Q05_WARM_REPLAY_FEASIBILITY_V1.md`

Preferred execution parent:

```text
hrl/awma-q05-translation-timeline-174new-v1
reported completion commit = 6319020c
```

Codex must first verify that the reported parent branch/commit is remotely resolvable. Do not silently replace provenance if it is not.

Recommended branch:

`hrl/awma-q05-warm-replay-feasibility-174new-v1`

Objective:

- source-audit all relevant state persistence/reset across kernel boundaries;
- reconcile 240 simulator keys vs 228 offline 64KiB pages;
- design Q05-only measurement by state-preserving counter deltas;
- qualify warm-state observability;
- use Q05->Q05 only as a self-warm plumbing diagnostic when safe;
- define the exact future same-run predecessor context-bundle contract.

Expected completion:

`AWMA_Q05_WARM_REPLAY_FEASIBILITY_174NEW_V1_COMPLETE_WITH_SCOPE`

---

## Frozen workload

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

target     = Q05_PREFILL_ATTN_FLASH
function occurrence = 0
```

Existing Q05 SIM_INPUT/SIM_BASELINE/SIM_RUN/SIM_EVIDENCE remain read-only.

---

## Mainline priority policy

The mainline has first claim on node109 GPU and node174-new.

While M1 is ACTIVE:

```text
NO LDC.U8 repair side lane
NO Qwen3/DeepSeek side campaign
NO unrelated NCU campaign
NO additional opportunistic selected-kernel capture
NO cleanup work that could interfere with mainline
```

A side task may run only after the active mainline explicitly releases the required resource and must be preemptible at a safe checkpoint.

The mainline must never wait for a side task.

---

## Existing side/support state

Accepted producer assets already durable on node164:

```text
PREFILL_GEMM_PRIMARY_1
DECODE_GEMV_PRIMARY_1
```

Decode Flash capture remains blocked at a real `LDC.U8` trace-grammar semantic gap. That repair is deferred.

Producer-side node164 data plane is qualified.

174 storage consumer/local-space audits are support closeouts and do not supersede the current mainline.

---

## Explicitly forbidden in this V1 stage

Do not automatically start:

- simulator-native predecessor-prefix capture campaign;
- new predecessor-prefix SIM_INPUT admission;
- scientific warm-prefix Q05 replay;
- L2-TLB lookup-latency sweep;
- PTW fixed-latency experiment;
- walker/count/capacity/page-size sweep;
- Segment;
- early outstanding-translation/coalescing mechanism;
- new cache/TLB mechanism.

The only new GPU profiling authorized is what M1 explicitly requires for Q05 context characterization.

---

## Execution policy

Routine engineering issues are solve-and-continue:

- source navigation;
- observer/parser work;
- exact target filtering;
- data-plane publication;
- Python analysis;
- build/log formatting;
- diagnostic output volume;
- Git/worktree handling.

Stop for scientific review if continuing would require:

- changing frozen workload identity;
- guessing Q05 identity;
- claiming page overlap equals TLB residency;
- stitching independent address spaces as same-run context;
- changing simulator TLB/cache/PTW timing/functionality;
- resetting warm state at the Q05 measurement boundary;
- weakening trace grammar or fabricating address/width fields;
- launching the real expensive predecessor capture/replay stage before both M1 and M2 are reviewed.

Each track independently:

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

After M1 and M2 complete, return both reports to ChatGPT. Do not auto-start the next stage.
