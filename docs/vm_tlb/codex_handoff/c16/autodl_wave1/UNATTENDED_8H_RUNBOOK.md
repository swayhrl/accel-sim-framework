# C16 unattended 8-hour orchestration

Purpose: keep the paid RTX3090 scientifically productive while the user is away, without inventing scenarios, weakening identity/hash gates, or conflating clean timing with diagnostic instrumentation.

## Fixed checkpoints at orchestration start

- A Wave-1 package publisher: `168c97148ef2bbfaf9bbe199414b0e7a5fc3ed1d`
  - P2 raw Qwen2.5-7B manifest: `c937590dd4ea2b4f6407db7d8b077ed263af3cbc14562ef34142aa834b133f26`
  - P3 Qwen2.5-7B-AWQ manifest: `704dc320a131e31a6d9fd11a8ac623318777c832b0b699241c5bf3f1c8beda1c`
- G runtime branch: `hrl/vm-c16-g-autodl-wave1-v0`
  - current remote head at runbook creation: `89d036276ac2429387fcab6db567bb6158274855`
  - formal standalone runtime source: `3f02eef6e0d00ea654821be8539bb82f463e87e5`
  - direct-semantic runtime source: `b241fecfe5cd78bc2cdbb733e3a437d68b741c89`
- P event-driven postprocess: `70a8191ef264d91db561115e25e57da953420f94`
- C Sampling-V2 waiting checkpoint: `29e669eca19ac3b2a1350bf2d097569a41f123e1`
- H memory-fingerprint offline checkpoint: `932c6fa44a4896265214fc2136e34698402a5c7f`

These are starting identities only. Every lane must consume later milestones by exact commit + manifest/hash, never by moving branch name alone.

## Global unattended rules

1. Normal engineering failures (path, resumable transfer, bounded tool invocation, deterministic local export, package import) should be investigated and retried with bounded attempts; do not stop at the first ordinary failure.
2. Scientific identity failures are fail-closed: revision/hash/token/dtype/backend/package mismatch, CPU offload, ambiguous semantic mapping, budget exhaustion, or unbound raw artifacts must not be repaired by changing the experiment.
3. Formal GPU measurements are exclusive. While `MEASUREMENT_ACTIVE` exists, no model transfer, large hash scan, SQLite export, compression, second scientific GPU job, or other host-heavy work may share the measurement window.
4. Between formal measurements, transfer/hash and local-result return are allowed. GPU and local CPU analysis should be pipelined, not serialized.
5. Large raw artifacts remain outside Git. Git carries identity, size, SHA256, producer/run identity, status and compact summaries only.
6. Every source/contract change that affects subsequent scientific runs must pass focused tests, commit/push first, and be named by the resulting run receipt.
7. Do not use resident mode during this unattended window. Current status remains `RESIDENT_MODEL_NO_GO_WITH_EVIDENCE; RESIDENT_REQUALIFICATION_DEFERRED`.
8. Do not launch new Accel-Sim/full-ROI work or new model revisions.

## Lane G: paid GPU queue

G should not wait for P or C analysis when another already-authorized GPU task is ready.

### G-1 close current Llama direct-semantic event

- Finish the current Llama S2 `SEMANTIC_DIAGNOSTIC_ONLY` closure.
- Semantic timing is never promoted into clean performance timing.
- Within the diagnostic report, direct module/NVTX temporal containment is allowed.
- Do **not** join diagnostic and clean reports by absolute timestamp. Cross-run clean↔diagnostic matching belongs to P and must follow P's event/join contract.
- Preserve full population and UNKNOWN rows. Current low direct coverage is a valid limitation, not a reason to guess labels.
- Publish compact semantic receipt/coverage/raw-index metadata and push a milestone commit.

### G-2 consume P3 AWQ first unless P2 is already actively transferring

After a formal measurement group ends:

1. Consume A@`168c9714...` P3 using the exact manifest SHA above.
2. Transfer between measurement groups only; full hash closure before GPU execution.
3. Commit/push a P3-consumption milestone.
4. Qwen2.5-7B-AWQ: G0 -> frozen baseline scenarios -> G1 census.
5. If a frozen scenario OOMs, record `SKIPPED_RESOURCE`; no CPU offload and no silent context/batch reduction.
6. Return each `.nsys-rep` quickly: remote SHA -> transfer -> local SHA confirmation -> raw index; then start next authorized GPU work without waiting for P's SQLite/catalog work.

### G-3 consume P2 raw

Repeat the same flow for raw Qwen2.5-7B P2. On RTX3090, resource admission is real; OOM is a result and must remain explicit.

### G-4 finish Qwen0.5 frozen native coverage

If S3/S4 are still incomplete, execute them when doing so does not delay an already transferred 7B deployment. Do not invent new scenarios.

### G-5 direct semantic diagnostics

After clean baseline/G1 exists for a deployment, a separate semantic diagnostic may be run for representative frozen scenarios. It must be:

- `SEMANTIC_DIAGNOSTIC_ONLY`
- `scientific_eligible_for_timing=false`
- direct module/NVTX evidence only
- no kernel-name/duration/history heuristic
- ambiguity -> UNKNOWN

Llama S2 semantic qualification is the template. For Qwen, run only after the clean performance path is already closed for the same deployment/scenario identity.

### G-6 implementation audit and Wave-1 producer closure

For each deployment, publish or explicitly mark unknown:

- attention backend actually used
- dtype/quantization implementation
- KV/runtime representation evidence available from the runtime path
- compile state
- GPU UUID/driver/runtime identity
- clean baseline/census receipts
- semantic diagnostic receipt/coverage if available

When P0-P3 have clean runtime coverage or explicit resource gaps, publish a hash-bound Wave-1 native producer checkpoint. It may be coverage-limited; do not wait for 95% semantic mapping if the limitation is explicit.

### G-7 G2/G3 only after frozen targets

G2/NCU and G3/NVBit remain nonblocking and must not be improvised. They may start only after C publishes a frozen target/sample plan with exact target identities. Before that, G should continue the authorized native/semantic queue above.

When C target plan appears:

- consume exact C commit + manifest/hash;
- execute bounded NCU first if authorized;
- execute NVBit only for frozen target windows and only under existing 4GiB/20min/64GiB/global budget guards;
- return tiny/selected trace promptly for H;
- no target expansion merely because GPU is idle.

## Lane P: event-driven local CPU pipeline

P should remain a separate local worktree/branch and may run concurrently with G.

Poll/inspect G remote milestones periodically with bounded cadence; do not consume live partial files. Resume only for complete events defined by P@`70a8191...`.

### P-event 1: new hash-closed `.nsys-rep`

For each complete G P1 event:

- require producer G full commit/manifest, run/deployment/scenario/input identity, raw path/size/SHA, transfer receipt, Nsight version and terminal status;
- local export using the qualified tool pair;
- preserve every launch;
- update `PROFILE_REPORT_INDEX`, raw index and `RUN_JOIN_AUDIT`;
- no naked stream/correlation cross-report join;
- large SQLite/TSV/gzip stay outside Git;
- milestone commit/push after each completed model/scenario batch, not each parsing step.

### P-event 2: direct semantic diagnostic

- verify diagnostic producer/run/report/hash closure;
- keep diagnostic timing non-scientific;
- construct `DIRECT_SEMANTIC_MAP.tsv` and `SEMANTIC_COVERAGE.tsv` from direct evidence;
- clean↔diagnostic cross-run association must use scoped structural identity and explicit ambiguity rules; never absolute timestamps alone;
- 0 or >1 eligible clean matches -> UNKNOWN;
- mapped coverage <95% is allowed only as explicit `COVERAGE_LIMITED`, never filled by heuristics.

### P-event 3: publish C-consumable native catalog

Once clean P0-P3 catalog data and direct semantic evidence are sufficiently bound for the available deployments, publish an immutable P checkpoint for C. It must include exact G producer commits, raw hashes, catalog hashes, semantic-map/coverage hashes, join contract and explicit per-deployment gaps.

This handoff may be partial/coverage-limited. UNKNOWN is a valid stratum. Do not block forever waiting for 95% semantic coverage.

## Lane C: downstream event-driven Sampling V2

C may be started now in waiting mode, but must not freeze from the old all-UNKNOWN provisional catalog.

When P publishes a C-consumable checkpoint:

1. Consume exact P commit + manifest/hash and exact underlying G producer identities.
2. Validate schema/join identities; repeats must not multiply logical population.
3. Freeze the native selector source SHA before reading holdout/target outcomes.
4. Build strata using the already-defined V2 contract. UNKNOWN semantic fields remain explicit strata; do not drop or heuristically relabel them.
5. Apply certainty-unit rules and strata-specific `N_s/n_s` estimator.
6. Publish frozen 12/24/48 plans and, when decision-ready, a bounded NCU/NVBit target plan.
7. Commit/push immediately when the target plan becomes consumable by G.

If semantic coverage is limited, C may still produce a coverage-limited plan using explicit UNKNOWN strata. It must downgrade interpretation rather than stall or invent labels.

## Lane H: optional trace event

H stays dormant until G publishes a hash-closed tiny/selected NVBit event. Then H may perform its already-qualified G->H manifest/SHA ingestion and memory fingerprint path. `TRACEG` remains `SET_ONLY`; VA buckets are not hardware TLB misses.

## Milestone push cadence

G/P/C must push when any of these becomes true:

- source/contract change affects future scientific execution;
- package consumption closes;
- G0/G1/G2/G3 state changes;
- a model/scenario batch closes;
- semantic GO/NO_GO/coverage status changes;
- a cross-lane consumable producer checkpoint appears;
- C freezes selector/target plan;
- resource/capability/budget state changes the path.

Do not push raw progress noise.

## End-of-window stop conditions

Continue until the earliest of:

- all currently authorized Wave-1 native/semantic work is closed and the pipeline is waiting only for an unavailable future input;
- execution budget is exhausted;
- a fail-closed scientific identity mismatch cannot be resolved without changing the experiment;
- provider/GPU capability prevents the authorized action after bounded attempts.

Before becoming idle, each active lane must push a final checkpoint and update its latest-status report with exact blockers and next action. Do not silently substitute a new model/config/target.