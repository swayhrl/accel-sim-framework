# C16 Unattended Formal Capture Policy V1

Ownership: ChatGPT
Purpose: allow a multi-hour node109 formal capture campaign to continue without operator intervention while preserving scientific identity and avoiding ad-hoc fixes.

## 1. Decision

A separate full seven-scenario native-rehearsal Codex is not required if pre-capture planning has already established model/runtime identity and the formal campaign performs an explicit resource-admission preflight before each selected scenario.

The campaign must never silently change model/input/runtime semantics to recover from a failure.

## 2. Per-scenario preflight before formal capture

For each selected model/scenario, in this order:

1. verify exact model revision and admitted asset receipt;
2. verify exact frozen input/token binding and scenario identity;
3. verify required runtime/dtype/backend contract;
4. acquire the node109 campaign GPU lock;
5. prove no unrelated GPU compute process is active;
6. run one native bounded smoke execution in a fresh process;
7. record peak GPU memory, exit status and output checksum/token IDs;
8. if the scenario is resource-admitted, proceed to target canary;
9. otherwise classify and continue according to the failure table below.

Do not retokenize and do not use CPU offload.

## 3. Target portfolio contract

Pre-capture planning must freeze an ordered target portfolio per model/scenario/phase. Each row must include:

- semantic stratum/role;
- exact function identity;
- code-object/static-map identity when available;
- selected launch or bounded launch selector;
- static GLOBAL MREF set or exact selected MREFs;
- duration contribution or other population evidence;
- NCU memory evidence where captured;
- target class: REPRESENTATIVE or CONTROL;
- ordered fallback candidates within the same semantic stratum;
- estimated time/size budget.

The formal campaign may move only to a pre-frozen fallback candidate. It may not discover a new arbitrary target during unattended execution.

## 4. Three-stage target execution

For every formal REPRESENTATIVE target:

### Stage A — identity canary

Run a no-payload or minimal-payload target identity diagnostic.

Require:

- expected function/launch observed;
- expected static target or MREF set resolves;
- model checksum remains stable;
- terminal/lifecycle closes normally.

### Stage B — tiny bounded trace canary

Collect a small bounded address-bearing sample sufficient to establish that the target is not trivially degenerate for the intended role.

Record at minimum:

- event count;
- drop/overflow count;
- nonzero address count;
- unique 128B lines;
- unique 4K pages;
- active-lane summary when available.

A REPRESENTATIVE candidate that unexpectedly collapses to an extremely narrow footprint must be marked `DEGENERATE_FOR_REPRESENTATIVE_USE` and replaced only by the next pre-frozen candidate in the same stratum. CONTROL targets may legitimately be narrow but do not satisfy phase-representative coverage by themselves.

### Stage C — formal bounded trace

Proceed only after A+B PASS.

Default per-target bounds:

- wall clock <= 20 min; OR
- produced raw <= 4 GiB;

whichever is reached first.

A clean bound hit is `BOUNDED_PARTIAL`, not an automatic failure. Finalize and publish it if the captured window is internally complete and hash-closed.

Initial total formal campaign raw budget: <= 64 GiB unless a later ChatGPT handoff changes it.

## 5. Failure handling table

### Exact model load OOM

Result: `NOT_ADMITTED_MEMORY` for that deployment/scenario on RTX4080.
Action: record peak/attempt evidence if available, skip it, continue the next frozen scenario/model.
Forbidden: changing dtype, quantization, context, batch, backend, or enabling CPU offload.

### Scenario-only OOM

Result: `SCENARIO_NOT_ADMITTED_MEMORY`.
Action: skip that scenario, retain the deployment for smaller already-frozen scenarios.

### Transient CUDA/runtime failure

Action: retry exactly once in a fresh process after proving the shared GPU lock and no unrelated GPU process. If repeated, mark `RUNTIME_UNSTABLE` and continue.

### Output checksum/token mismatch

Action: invalidate the run and retry once with the identical command and inputs. Repeated mismatch => `OUTPUT_UNSTABLE`, skip that scenario. Never accept a trace with mismatched output identity.

### Target function/static identity not found

Action: try the next pre-frozen candidate in the same semantic stratum. If all fail, mark the stratum `TARGET_IDENTITY_UNRESOLVED` and continue.

### Target observed but zero address-bearing trace

Action: one identical fresh-process retry; then try the next pre-frozen candidate. No ad-hoc target discovery.

### Drop/overflow observed

Action: halve the bounded launch/window size and retry once on the same target. If still nonzero, classify `TRACE_OVERFLOW_BOUNDED_INCOMPLETE`, preserve diagnostics, continue to the next target.

### Formal size/time bound reached

Action: stop cleanly, finalize as `BOUNDED_PARTIAL`, publish, continue.

### Pipeline transfer failure / 174 unavailable

Action: retain the locally finalized `ready/<RUN_ID>` bundle and retry transport only. Do not rerun the GPU capture. The campaign may continue new captures only while local free-space/campaign budget remains safe.

### Destination verification failure

Action: no ACK. Keep/quarantine destination partial as Pipeline V1 defines. Retain producer source and continue only after transport state is safe.

## 6. Ordering / interference rules

- Only one node109 formal GPU producer action at a time.
- Do not overlap formal native timing or NCU capture with bulk data transfer.
- Do not overlap NVBit formal capture with another profiler/capture window.
- After a capture is closed, transport may run before the next formal measurement, or be queued when doing so does not risk local space.
- 174-new analysis may run concurrently because it is CPU-side and uses admitted data only.

## 7. Scenario efficiency policy

Do not formally trace all seven historical scenarios by default.

Use pre-capture planning to choose the minimum set that answers the intended axes. Expected first-wave priorities are:

- `S2_TEXT`: main representative scenario;
- `S3_TEXT`: long-context sensitivity when resource-admitted;
- `S4_STRUCTURED`: batch sensitivity when resource-admitted;
- one controlled shape-matched CODE/STRUCTURED/TEXT comparison only if native/kernel census shows a meaningful implementation difference;
- `S0/S1`: smoke/control unless scientifically needed.

If S2_CODE/S2_STRUCTURED/S2_TEXT have the same kernel signature and launch population for a deployment, do not duplicate full NVBit captures solely because the text content differs. Preserve one audit scenario if desired.

## 8. First-wave model order

Unless pre-capture planning gives a stronger reason:

1. Qwen2.5-0.5B-Instruct;
2. Qwen2.5-7B-Instruct-AWQ;
3. Qwen2.5-7B-Instruct raw only if exact resource admission passes;
4. Llama-3.2-1B high-quality supplemental capture;
5. Qwen3-8B / DeepSeek only after explicit prospective input authority and resource admission.

## 9. Publication requirement

Every accepted trace must pass Pipeline V1:

capture staging -> local finalize -> ready -> copy to 174/164 inbox.partial -> independent destination rehash -> immutable catalog -> ACK -> producer transferred.

Scientific identity is carried by RUN_MANIFEST + receipts + hashes, not by filename alone.

## 10. Final unattended campaign report

At the end, report every attempted matrix row, including failures. Required status classes include:

- FORMAL_COMPLETE
- BOUNDED_PARTIAL
- NOT_ADMITTED_MEMORY
- RUNTIME_UNSTABLE
- OUTPUT_UNSTABLE
- TARGET_IDENTITY_UNRESOLVED
- DEGENERATE_FOR_REPRESENTATIVE_USE
- TRACE_OVERFLOW_BOUNDED_INCOMPLETE
- TRANSFER_PENDING

Never omit failed/skipped rows in a way that makes campaign coverage appear higher than it was.
