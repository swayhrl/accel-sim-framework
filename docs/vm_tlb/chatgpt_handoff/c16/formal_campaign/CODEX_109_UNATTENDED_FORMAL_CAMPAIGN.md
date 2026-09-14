# CODEX GOAL — C16 RTX4080 Unattended Formal Trace Campaign V1

Owner: ChatGPT
Execution node: node109 / RTX4080
Required execution style: **Goal mode**
Expected duration: multi-hour, unattended

## Goal statement

Deliver the first high-quality formal C16 cross-model memory-trace corpus from the admitted RTX4080 deployments.

This task is **not** “run the already-ready matrix rows”. The pre-capture matrix currently has zero rows marked ready for formal trace because readiness work was intentionally left fail-closed. Your job is to **solve the readiness gaps and then perform the formal captures in the same Goal**, while preserving scientific identity.

Do not stop after reporting that object maps/static maps/NCU/semantic labels are missing. Treat those as work items.

Do not lower scientific quality merely to make a trace appear.

## Read first

Read in this order:

```text
docs/vm_tlb/chatgpt_handoff/c16/formal_campaign/FORMAL_CAMPAIGN_MASTER_GOAL_V1.md
docs/vm_tlb/chatgpt_handoff/c16/formal_campaign/READINESS_RECOVERY_PLAYBOOK_V1.md
docs/vm_tlb/chatgpt_handoff/c16/formal_campaign/CAPTURE_EXECUTION_AND_ACCEPTANCE_V1.md
```

Then inspect the pre-capture review pack from:

```text
55d11e6829bc89189d1c3fadf695c31078485421

docs/vm_tlb/review_packs/C16_TRACE_CAMPAIGN_PRECAPTURE_109_V1/
```

Important accepted infrastructure anchors:

```text
Pipeline V1 integration:
3c4847d2da818013dca6422194af36966136ab31

Analysis prep:
d07b7eb5d43b9a31474a6d298ec4e4f75292cc48

Pre-capture matrix freeze:
a5ab72e99976abb9f4592176c280defe8f75f9af
```

## Branch / worktree

Create a fresh execution worktree from the coordination branch you fetched.

Suggested branch:

```text
hrl/c16-formal-trace-campaign-109-v1
```

Do not modify ChatGPT-owned handoff files.

Do not replace accepted Pipeline V1 code with the older pre-capture branch implementation.

Bring in the pre-capture **review pack/evidence only** with a path-scoped checkout or equivalent, for example:

```bash
git fetch origin
git checkout 55d11e6829bc89189d1c3fadf695c31078485421 -- \
  docs/vm_tlb/review_packs/C16_TRACE_CAMPAIGN_PRECAPTURE_109_V1
```

If additional pre-capture scripts are needed, inspect them selectively; do not wholesale overwrite `util/vm_tlb/c16/data_plane/`.

## GPU lock

Every GPU action must acquire:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

CPU-only work may proceed without it.

Do not kill unrelated processes automatically. If unrelated GPU compute is present, wait/recheck and record it; only proceed when the device state is scientifically interpretable.

## Execution phases

### Phase 0 — bootstrap and campaign state

- verify exact repo/worktree/commit state;
- verify Pipeline V1 commands/code available;
- verify NVBit 1.7.5 pinned tool identity;
- verify NCU authority `/opt/nvidia/nsight-compute/2025.1.1/ncu`;
- verify NSYS;
- create/update `/data/c16/results/C16_FORMAL_CAMPAIGN_V1/CAMPAIGN_STATE.json`;
- import the pre-capture matrix as the starting candidate set, not as a terminal blocker.

### Phase 1 — Qwen2.5-0.5B readiness recovery

Using exact S2_TEXT frozen authority:

1. build/hash-close runtime object map;
2. retain the existing exact Prefill GEMM static map;
3. close missing Prefill attention static map/selector evidence;
4. close Decode heavy + memory/KV/attention target identities/static maps;
5. refine semantic labels only where evidence supports them;
6. obtain bounded NCU evidence for top targets where practical;
7. run address-bearing canaries on exact targets;
8. reject trivial/mis-selected canaries and use same-stratum fallbacks;
9. promote scientifically qualified targets to formal readiness.

Do not require a GEMM to be proven “FFN” before capturing it if exact heavy-GEMM identity/importance is already established. Keep `GEMM_HEAVY_UNRESOLVED_SEMANTIC` when needed.

### Phase 2 — Qwen2.5-0.5B formal capture

Capture the S2 core portfolio in value order:

- Prefill heavy GEMM;
- Prefill attention core;
- Decode early heavy target;
- Decode early memory/KV/attention target;
- Decode late memory/KV-sensitive counterpart if useful;
- representative audit/control only after core targets.

For each accepted target:

```text
preflight
-> exact selector revalidation
-> address-bearing canary
-> quick footprint quality check
-> formal bounded NVBit
-> local finalize
-> Pipeline V1 publish
-> 174 verify/catalog/ACK
-> node109 ACK verify / transferred
-> checkpoint CAMPAIGN_STATE
```

Do not wait for all Qwen0 targets before publishing the first completed run.

### Phase 3 — Qwen2.5-7B-AWQ readiness recovery

Exact deployment identity is the actually observed:

```text
qwen25_7b_awq_autoawq_unfused
```

Do not install/change backend in-place and do not claim fused equivalence.

Within the same Goal:

- build AWQ object map including packed weight and quant metadata ranges;
- create RTX4080-local exact static maps for the high-value S2 targets;
- characterize top candidates with bounded NCU where useful;
- create exact Prefill/Decode launch selectors;
- run address-bearing canaries;
- choose same-stratum fallbacks when a candidate is weak.

### Phase 4 — Qwen2.5-7B-AWQ formal capture

Prioritize:

- Prefill dominant quantized GEMM / weight-heavy target;
- quant/dequant or metadata-related stratum if distinct and important;
- attention core;
- Decode heavy target;
- early/late decode KV/attention-memory target where useful.

Use the same finalize/publish/ACK/checkpoint lifecycle as Qwen0.

### Phase 5 — targeted context/batch/content controls

Do lightweight native/NSYS checks for frozen S1/S3/S4 and content variants.

Do **not** large-trace every scenario by default.

Add formal controls when the runtime shows scientifically meaningful differences (new memory kernel class, shape, long-context/KV behavior, batch implementation change, etc.).

Strong preference if resource-admitted:

- at least one S3 long-context attention/KV-sensitive control for Qwen0;
- analogous S3 control for AWQ when stable;
- one S4 batch control where implementation changes materially.

If a scenario is redundant, record it as `CONTROL_ONLY / NO_MATERIAL_KERNEL_CHANGE` rather than forcing a large trace.

### Phase 6 — raw Qwen2.5-7B exact resource retry

After Qwen0/AWQ core capture is already safe, retry exact S2_TEXT admission in a fresh idle process.

Do not change scientific configuration.

If admitted, run a lightweight census and capture a minimal high-value portfolio only if time/storage allow.

If two clean exact attempts still OOM, record `NOT_ADMITTED_MEMORY_CONFIRMED` and continue.

### Phase 7 — Llama S0 high-quality supplement

Use the exact accepted Llama S0 authority available on node109.

Do a compact high-quality RTX4080-local target-selection/canary/capture loop using all relevant GLOBAL MREFs of selected exact launches.

The purpose is to produce better analyzable evidence than the historic easy-PC style traces.

Keep scope explicitly `S0_ONLY`.

### Phase 8 — campaign closeout

- ensure every accepted run has Pipeline V1 ACK closure;
- retry transfer-only for any locally closed bundles whose remote transfer failed;
- build final indexes/review pack;
- independently validate review-pack SHA256SUMS;
- clean Git status;
- commit/push;
- STOP.

## Do not use these as meaningless blockers

The following must not cause an immediate campaign stop by themselves:

- pre-capture row not already labeled `READY_FOR_FORMAL_TRACE`;
- semantic role of an exact heavy GEMM still unresolved;
- no NCU row for every target;
- partial object attribution when known weights/KV/quant metadata are mapped and UNKNOWN is preserved;
- one target is weak;
- one scenario is OOM;
- one deployment is deferred;
- a parser on 174 needs adaptation after raw is safely admitted.

Solve or classify, then continue.

## Hard prohibitions

Never:

- retokenize a historical frozen Qwen binding;
- silently alter model revision/scenario/dtype/backend/quantization;
- CPU-offload to make a formal deployment fit;
- replace a representative target with an arbitrary easy memory PC;
- call unfused AutoAWQ fused;
- infer Qwen3/DeepSeek historical input authority;
- delete source raw after transfer;
- overwrite immutable node164 admitted runs/catalog entries;
- run multiple node164 formal admission writers concurrently.

## Autonomous recovery behavior

Use the playbook. In general:

- transient/runtime failure -> diagnose and fresh-process retry;
- exact target issue -> repair identity/static map or use same-stratum fallback;
- trace size/slow -> reduce complete launch/window count, not to one arbitrary PC;
- zero-address -> validate selector/tool, retry once, then fallback;
- transfer failure -> retry transport only;
- parser failure -> preserve raw and repair analysis separately.

Do not repeat an identical failed command indefinitely. Every retry beyond the first should test a concrete new hypothesis.

## Soft campaign budgets

Use the planning defaults as soft controls:

- approximately `<=4 GiB` raw per target;
- approximately `<=20 min` per target;
- approximately `<=64 GiB` first-wave raw total.

Do not stop a scientifically important campaign merely because a soft estimate is exceeded slightly. Instead avoid starting low-priority controls when capacity/time becomes tight.

Never accept a mid-launch truncation as formal just to satisfy a bound.

## Required output / review pack

Create:

```text
docs/vm_tlb/review_packs/C16_FORMAL_TRACE_CAMPAIGN_109_V1/
```

with at least all files listed in `CAPTURE_EXECUTION_AND_ACCEPTANCE_V1.md`.

The final report must separately state:

- Qwen0 formal representative coverage;
- AWQ formal representative coverage;
- context/batch/content controls captured or deferred;
- raw7B admission result;
- Llama S0 supplement result;
- all recovery actions attempted;
- all rejected/weak targets and why;
- total GPU/profile/capture wall time;
- total raw bytes;
- every node164 admitted run path + manifest/ACK identity;
- any remaining gaps that actually affect scientific interpretation.

## Acceptance / completion

Aim for:

`FORMAL_CAMPAIGN_PASS`

A legitimate completion may be:

`FORMAL_CAMPAIGN_PASS_WITH_DEFERRED_CONTROLS`

or:

`FORMAL_CAMPAIGN_PARTIAL_WITH_ROOT_CAUSE`

Do not return `PASS` merely because the pre-capture matrix stayed empty. A successful Goal must produce useful formal traces or an evidence-backed global root cause demonstrating why a core deployment could not.

## STOP boundary

STOP only after the Goal has reached a final campaign outcome, the review pack is complete/hash-closed, and the branch is pushed.

Do not pause for intermediate approval after each target/problem. Continue autonomously unless proceeding would require violating a scientific invariant or an unresolved global infrastructure/authority failure makes further trustworthy work impossible.
