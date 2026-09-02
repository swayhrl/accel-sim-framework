# AGENTS.md — VM/TLB Research Project Guardrails

This file is authoritative for Codex/agent work on branch `hrl/vm-core-v0` and descendants used by the VM/TLB project.

## 1. Project purpose

Build a research-grade GPU virtual-memory substrate in Accel-Sim/GPGPU-Sim, then use it to reproduce and study GPU address translation for AI workloads, beginning with `Towards Segmentation-Based Address Translation for LLM Inference`.

The implementation sequence is intentionally staged:

1. VM-core foundation and address-space contract.
2. Single-GPU L1/L2 TLB + translation-MSHR + PTW baseline.
3. Timing-realistic PTE/L2/DRAM path and validation.
4. LLM trace/metadata preparation and paper reproduction.
5. New AI-aware TLB research only after the reproduction baseline is frozen.

Do not skip stages because a later mechanism appears easy to implement.

## 2. Frozen source anchors

Framework baseline:
`3016c658f810bdae9a14bf4534ee99e9945eedae`

Core/GPGPU-Sim baseline:
`73774727e25fadf89df6f30ef5cf014091115db7`

Framework research branch:
`hrl/vm-core-v0`

Core research repository:
`swayhrl/gpgpu-sim`

Core research branch:
`hrl/vm-core-v0`

The TLS/MCM implementation and legacy `dev-uvm` branch are reference sources only unless a current `CODEX_NEXT_STAGE.md` explicitly authorizes selective reuse. Do not cherry-pick them wholesale.

## 3. Source-of-truth and handoff ownership

Project coordination lives under:

`docs/vm_tlb/`

Read in this order before every new task:

1. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. `docs/vm_tlb/chatgpt_handoff/CODEX_NEXT_STAGE.md`
4. this `AGENTS.md`

Ownership:

- `chatgpt_handoff/*` is ChatGPT-owned. Codex must not modify it unless the current stage specification explicitly grants permission.
- `codex_handoff/*` is Codex-owned execution reporting, subject to the report path assigned by the current stage.
- `review_packs/<stage>/` is Codex-generated review evidence.
- Long-lived architecture/specification documents may be modified only when the current stage explicitly authorizes them.

When multiple Codex windows run in parallel, they must use separate track-specific report paths assigned by `CODEX_NEXT_STAGE.md`; do not let both branches overwrite the same active `LATEST_REPORT.md`. The root bootstrap report may remain historical.

A chat message is not a substitute for committed handoff state when the two disagree. Stop and report the conflict.

## 4. Research evidence labels

Use these labels consistently:

- `VERIFIED_CODE`: established directly from source at recorded SHA.
- `VERIFIED_RUN`: established by a recorded build/run at recorded SHA/config/trace.
- `PAPER_SPEC`: explicitly stated by the target paper.
- `USER_CONFIRMED`: supplied by the user but not independently verified in the repository.
- `MODELING_DECISION`: deliberate simulator contract, not claimed hardware fact.
- `HYPOTHESIS`: research hypothesis requiring experiment.
- `UNKNOWN`: unresolved.

Never silently upgrade `UNKNOWN`, `HYPOTHESIS`, or `MODELING_DECISION` into a hardware fact.

For paper reproduction also distinguish:

- `PAPER_EXACT`: implementation detail is directly supported by paper/artifact/source.
- `DOCUMENTED_APPROX`: paper detail is unavailable and an explicit approximation has been approved.

Codex must STOP before converting a required `PAPER_EXACT` item into `DOCUMENTED_APPROX` unless the stage spec already authorizes that approximation.

## 5. Core VM semantic guardrails

Unless a later approved specification supersedes them, preserve these project contracts:

### 5.1 Address naming

Treat the trace address as simulator input address `SimVA` by modeling contract. Do not claim this proves the exact internal NVIDIA hardware VA stage captured by NVBit.

Translation produces `SimPA`.

Preserve both identities for observability; do not overwrite the only copy of the original address with the translated address.

### 5.2 Identity-mapping bring-up

The first functional mapping mode is identity-like at page granularity so that data-cache/DRAM locality remains unchanged:

`SimPPN = SimVPN` and therefore data `SimPA == SimVA` for the baseline mapping.

With ideal translation + identity mapping enabled, all non-VM architectural behavior must match the VM-disabled baseline, subject only to explicitly documented logging/statistics differences.

### 5.3 Translation placement

Do not implement per-lane TLB accesses by default. Translation is expected to operate on coalesced memory transactions (`mem_access_t` or the approved equivalent) before the real L1D/data-cache access.

If a coalesced transaction can cross a base-page boundary, prove it with a directed test and implement the required split; do not guess.

### 5.4 Resident-memory baseline

M1–M3 study address translation, not residency management.

Unless explicitly authorized:

- all application pages are present before execution;
- no GPU page faults;
- no CPU fault service;
- no page migration;
- no UVM oversubscription mechanism.

### 5.5 TLB lifetime

Default modeling decision: translations persist across ordinary kernels in the same simulated context. Do not flush TLB state at every kernel boundary unless a later approved model requires it.

Flush/invalidate only on explicitly modeled reset, mapping invalidation/remap, context change, or approved mechanism.

## 6. Correctness invariants

The following are hard correctness requirements once the corresponding components exist:

- A PTE-memory request is already physical and must never recursively enter normal address translation.
- One `(ASID, VPN, page-size-class)` may have at most one active page walk at a time; later misses must merge or backpressure according to the frozen MSHR policy.
- Translation-MSHR merge is not a TLB hit.
- A waiter is registered once and awakened once.
- A translation fill must not duplicate/reissue a store or atomic side effect.
- Real data-cache access must not occur before the required translation has completed.
- Queue/walker/MSHR capacity limits must be enforced, not represented only as statistics.
- `active_walkers <= configured_walkers` at all times.
- No request may disappear at simulation completion; outstanding-request conservation must be checkable.
- When VM is disabled, VM code must not add latency, queuing, mapping changes, or side effects.

A failure of any of these invariants blocks performance characterization.

## 7. Implementation discipline

Prefer minimal semantic changes over large refactors.

Do not combine structural cleanup and new functional behavior in one commit unless unavoidable and documented.

Do not add speculative safety behavior that changes the intended protocol. If an upstream contract is assumed, encode it as an assertion or validation check when practical.

Do not weaken or delete a directed test merely to make a stage pass.

Do not replace a cycle/resource model with a fixed latency when the stage requires a real queue/port/resource model.

Legacy UVM/TLB code may be read for interface ideas, but its behavior is not automatically authoritative.

## 8. Statistics and observability

Statistics are part of the research implementation, not optional debug printouts.

Prefer structured counters/CSV/TSV over ad-hoc log parsing.

Keep at least these concepts separable when implemented:

- L1 TLB access/hit/miss;
- L2 TLB access/hit/miss;
- translation-MSHR allocation/merge/full stall;
- page-walk queue delay;
- walker service time/utilization;
- PWC behavior;
- PTE requests by page-table level and cache/DRAM outcome;
- translation-caused blocked-warp cycles;
- fill/replay latency;
- page size;
- object type when LLM metadata is enabled;
- synthetic versus real requests.

Do not report a synthetic KV translation request as a real GPU instruction or ordinary data access.

## 9. Validation policy

Every semantic stage needs directed tests before integrated workload experiments.

Tests must assert expected counts/invariants, not merely exit code 0.

For performance experiments, always record:

- Core SHA;
- Framework SHA;
- config identity/SHA;
- trace identity/SHA where practical;
- metadata/sidecar identity when used;
- run status (`FORMAL`, `DIAGNOSTIC`, `PRE_FIX`, `OBSOLETE`);
- exact command and wall-clock.

Never mix PRE_FIX/OBSOLETE results into formal analysis after a correctness change.

## 10. Git/worktree policy

Use isolated branches/worktrees for new macro stages when requested by the handoff.

Never modify a frozen baseline worktree that is being used by another experiment.

Forbidden:

- `git add .`
- `git add -A`
- force-pushing shared research history unless explicitly authorized
- pushing to the official upstream Accel-Sim/GPGPU-Sim repository

Stage only explicit paths.

Keep commits semantic and reviewable.

Before closeout run at minimum:

- relevant build/tests;
- `git diff --check`;
- `git status --short`;
- provenance capture.

If a source repository has no verified writable remote, stop before source modification unless the user/ChatGPT explicitly resolves the remote.

## 11. Review-pack requirements

Each completed stage must create/update:

`docs/vm_tlb/review_packs/<stage>/`

The pack must be sufficient for independent review without relying on Codex chat text. At minimum include:

- `README.md` as the sole recommended entry;
- source anchors;
- commit history;
- changed files/diff summary;
- validation summary;
- open issues;
- raw-log index rather than large raw logs.

For functional VM stages also include or link machine-checkable invariant results and representative structured statistics.

Update the **track-specific Codex report path assigned by the current `CODEX_NEXT_STAGE.md`** at stage completion.

## 12. STOP policy for long target-mode tasks

A macro task may contain multiple approved sub-stages and Codex may continue automatically only when each sub-stage passes its own acceptance criteria.

STOP and report immediately when:

- a correctness invariant fails;
- baseline transparency fails;
- a required paper detail is ambiguous and materially changes the design;
- a required `PAPER_EXACT` detail cannot be obtained and approximation has not been authorized;
- deadlock, lost request, duplicate wakeup, duplicate store/atomic, or unexplained nondeterminism appears;
- source provenance is uncertain;
- a required writable remote is unavailable;
- the next macro task has not been explicitly authorized.

Do not continue into performance characterization while correctness is unresolved.

## 13. Time/run discipline

Do not let a stuck command consume the session indefinitely.

For a command with no useful progress, record and reassess around 20 minutes; obey stricter stage-specific 20/40/60-minute limits when present in the handoff. Long formal runs must have explicit provenance and a reason to continue.

## 14. LLM reproduction boundary

The target paper uses a short real LLM simulation plus synthetic KV translation pressure for long-context emulation. Do not assume a public exact trace exists.

LLM reproduction must keep these artifacts distinct:

- real instruction/memory trace;
- allocation/tensor metadata sidecar;
- synthetic KV translation stream;
- contiguous-weight mapping policy;
- paging/sub-entry baseline;
- segmentation mechanism.

Weight, KV-cache, activation, workspace, unknown, and synthetic-KV classifications must not be conflated.

The paper PDF itself may be used locally for research, but do not commit copyrighted paper PDFs to the public repository unless explicitly authorized and legally appropriate. Commit bibliographic metadata and extracted reproduction specifications instead.

Real rented-GPU capture is a separate operational stage from pre-capture preparation. If the current handoff authorizes only pre-capture work, Codex must finish a ready-to-run capture package and STOP before starting an external rental/capture session.

## 15. Trace capture hardware guardrails

Always distinguish **tracer compatibility** from **simulator target compatibility**.

For the current Segmentation-paper reproduction, the intended simulated target is RTX3070-class / SM86. Prefer SM86 capture hardware and do not silently replay a trace from a different SASS generation as SM86.

For future Accel-Sim 2.0 AI-TLB work, a GPU that NVBit can instrument is not automatically a validated simulator target. In particular, RTX5090/Blackwell capture-tool support does not by itself authorize treating an RTX5090 trace as an H100/H200 trace. Follow the current Accel-Sim release support and the approved stage hardware matrix.
