# CODEX_NEXT_STAGE

Status: **ACTIVE MAINLINE — M3 + M4**

Stage:

`AWMA_Q05_CONTIGUOUS_PREFIX_WARM_REPLAY_V1`

Coordination branch:

`hrl/awma-q05-contiguous-prefix-warm-replay-handoff-v1`

All Codex instances read in order:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute only the relevant node-specific stage.

---

## M3 — node109 / RTX4080 — ACTIVE MAINLINE

Execute:

`CODEX_NEXT_STAGE_109_Q05_CONTIGUOUS_PREFIX_CAPTURE_V1.md`

Execution parent:

```text
hrl/awma-q05-native-context-109-v1
64a2e51943a6737b84132bc7daa5f4d7c74f8099
```

Recommended branch:

`hrl/awma-q05-contiguous-prefix-capture-109-v1`

Objective:

- minimally extend accepted Route-B single-target producer for same-run multi-member capture;
- regression one-target Q05;
- prove a two-member launches33..34 canary;
- capture formal launches0..34 context bundle;
- derive P1/P2/P4/P8/P16/P34 page-overlap tables offline;
- publish bundle to node164 with verify/admit/ACK.

This track owns the RTX4080 while ACTIVE.

Do not repair the old lightweight page observer as the main path.

Expected complete marker:

`AWMA_Q05_CONTIGUOUS_PREFIX_CAPTURE_109_V1_COMPLETE_WITH_SCOPE`

---

## M4 — node174-new — WAITING_FOR_CONTEXT_BUNDLE

Execute:

`CODEX_NEXT_STAGE_174NEW_Q05_WARM_PREFIX_REPLAY_V1.md`

Execution parent:

```text
hrl/awma-q05-warm-replay-feasibility-174new-v1
e2fa35f045e0b4f977a964d9c92974c9f6d3e240
```

Recommended branch:

`hrl/awma-q05-warm-prefix-replay-174new-v1`

Before bundle arrival, M4 preparation has already completed and closed cleanly as WAITING. Do **not** launch another Codex round solely to polish small wording/classification details. Fold those known, correctness-neutral edits into the next M4 resume when the formal M3 bundle is available.

After M3 durable+ACK:

- independently verify all 35 members/order/context;
- create a new context-input identity;
- run fresh-process P1/P2/P4/P8/P16/P34 + Q05 rows;
- report Q05-only translation and data-cache counters.

If M3 is not yet available after preparation, close cleanly as:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_WAITING_FOR_CONTEXT_BUNDLE`

Expected final marker:

`AWMA_Q05_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

---

## Mainline priority

No side task may delay M3/M4.

While M3 needs the GPU:

- no LDC.U8 side repair;
- no Qwen3/DeepSeek;
- no unrelated NCU;
- no extra selected-kernel campaign.

When M3 releases the GPU, side work still requires explicit authorization; do not auto-start it.

## Frozen science

The Qwen2.5-0.5B S2_TEXT/Q05 identity and existing isolated SIM_INPUT/baseline/run/evidence remain immutable.

The new context bundle/context-input is a new identity and must never overwrite the historical isolated-Q05 identity.

## Explicitly forbidden

Do not automatically start:

- TLB/PTW/cache mechanism design;
- latency/capacity/walker/page-size sweeps;
- Segment;
- target-only I0 warm-context mechanism experiment;
- full-model new campaigns;
- deletion/reorganization of accepted node164 evidence.

## Execution policy

Efficiency rule: do not spawn a standalone Codex stage for a correctness-neutral micro-fix whose safe resolution is already known. Fold it into the next substantive handoff/resume or let ChatGPT update coordination material directly.

Routine engineering is solve-and-continue.

Stop for scientific review on:

- sequence/address-context contradiction;
- unsupported interior trace grammar;
- trace semantic weakening;
- F0 state-semantic change;
- missing interior predecessor;
- resource guard partial capture;
- inability to separate Q05 statistics without reset.

Each track:

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
