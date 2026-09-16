# CODEX GOAL — 174-new Simulation Consumer Preparation V1

## Execution mode

Run this Goal on **174-new / SSH port 2239** in a **new Codex window with no assumed chat context**.

This Goal is deliberately self-contained. Read this file first, then the referenced coordination documents. Do not assume knowledge from an earlier Codex window.

Suggested working branch:

```text
hrl/awma-sim-consumer-prep-174new-v1
```

Recommended starting authority:

```text
coordination branch:
hrl/awma-sim-compat-capture-v1-coordination

accepted simulation baseline branch:
hrl/awma-new-sim-baseline-174new-v1

accepted simulation baseline commit:
2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49
```

Do not use node109 in this Goal. Node109 is currently allowed to remain occupied by another project task. This Goal must complete everything that is independent of the future producer capture and then stop cleanly at a consumer-ready checkpoint rather than idling or polling for node109.

---

# 1. Project context

This repository carries two distinct evidence planes for the AI-workload project:

```text
Native Characterization
  = measurements/captures from real GPU execution

Simulation Analysis
  = simulator-native trace + qualified simulator/runtime
```

These two planes may refer to the same workload/target identity, but their raw trace formats and semantics are not interchangeable.

The current Native C16 format (`C16WARP1` plus MREF-sharded data) is **not proven lossless as a simulator input** because it does not establish all simulator-required global instruction/temporal ordering and related semantics across MREF shards. Therefore:

```text
DO NOT convert, concatenate, infer, or synthesize C16WARP1/MREF data into traceg.
```

A future node109 stage will rerun the exact accepted current-model workload/target through a simulator-native tracer and produce a separate formal simulation-input bundle.

This 174-new Goal prepares the consumer side before that producer bundle exists.

---

# 2. Accepted baseline state entering this Goal

The previous simulation-foundation stage is accepted as:

```text
NEW_SIM_BASELINE_V1_QUALIFIED
scope = HASH_BOUND_FIXED_WINDOW_10000
```

It established that historical C12 formal Prefill and Decode trace inputs can be recovered under hash closure and replayed through the recovered historical Framework/Core source pair for a bounded 10,000-cycle window with non-zero VM/TLB/PTW/cache telemetry.

Historical source authority:

```text
Framework commit:
d64408a97d76a320a6d49468653d416e33677af8

Core commit:
57bb71ecd015b6ec0ab32e45b0815e5beaf69172
```

Historical formal C12 compute-list identities:

```text
Prefill:
a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f

Decode:
b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc
```

Recovered-view membership recorded by the accepted addendum:

```text
Prefill members: 692
Decode members: 740
```

Accepted bounded raw replay log hashes recorded by the previous stage:

```text
Prefill:
97daa2f73e34a61ba9a9d2a5f820740e8cd8671f05615ebb7009a51a2ea93c7f

Decode:
f80d97e98c96ca07431f15338af9fb1c547250d4fe6a9285dc35fdf540ac2cab
```

The accepted scope is intentionally narrow. It does **not** claim:

```text
historical simulator binary identity;
full-ROI replay equivalence;
exact historical numerical equivalence;
whole-model performance equivalence.
```

The accepted baseline report/review evidence is under:

```text
docs/vm_tlb/review_packs/AWMA_NEW_SIM_BASELINE_174NEW_V1/
docs/vm_tlb/codex_handoff/awma/NEW_SIM_BASELINE_174NEW_REPORT.md
```

Use those files as the source of truth when any summary text disagrees with earlier stale blocked-state text.

---

# 3. Known control-plane inconsistency to repair

The final baseline decision is qualified, but several older files in the same review pack may still contain the pre-recovery `BLOCKED_INPUT_OR_RUNTIME` state.

Audit at least:

```text
C12_PREFILL_CALIBRATION.tsv
C12_DECODE_CALIBRATION.tsv
SMOKE_LADDER_RESULTS.tsv
OPEN_ISSUES.md
EXTERNAL_BLOCKER.md
```

Reconcile them against successful evidence already present in:

```text
HISTORICAL_TRACE_RECOVERY_ADDENDUM.md
BASELINE_QUALIFICATION_DECISION.json
NEW_SIM_BASELINE_174NEW_REPORT.md
```

Rules:

1. This is a **documentation/control-plane repair**, not a new C12 experiment.
2. Do not rerun C12 solely to rewrite stale prose/TSV when existing raw/receipt evidence is sufficient.
3. Do not strengthen the scientific claim beyond `HASH_BOUND_FIXED_WINDOW_10000`.
4. Regenerate the baseline review-pack `SHA256SUMS` after justified edits.
5. Record exactly what was changed and why in this Goal's own review pack.

---

# 4. This Goal's exact objective

Complete all 174-new work that can be done before node109 produces a new simulator-native current-model trace.

Required terminal state for this Goal:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
```

This means:

```text
baseline identity frozen;
stale control-plane summaries reconciled;
consumer/admission contract implemented or hardened;
real traceg grammar/parser smoke available;
negative tests fail closed;
historical trace fixture passes as a regression fixture;
SIM_INPUT / SIM_RUN catalog schemas prepared;
runtime wrapper for future 10k-cycle replay prepared;
future producer handoff requirements made explicit;
no node109 dependency remains except the actual future producer bundle.
```

Do **not** wait for node109. If node109 has no READY bundle at the end, stop successfully at `174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1`.

---

# 5. Environment and role boundaries

Node role:

```text
174-new / port 2239
role = ingest + analysis + catalog + simulator consumer
```

Durable storage root used elsewhere in the project:

```text
/root/share/mnt164/huangrulin/c16_ai_workload
```

Historical simulation inheritance namespaces may already exist under that tree. Discover and reuse accepted canonical paths rather than creating competing roots.

Repository path can vary between a main checkout and Codex worktree. Detect the active repo root with Git; do not hard-code an unverified worktree path.

This Goal must not:

```text
SSH into node109 to control GPU work;
acquire the 109 GPU campaign lock;
kill/restart any 109 process;
run a new GPU capture;
modify Native raw evidence;
run TLB/Segment/cache optimization sweeps.
```

---

# 6. Required read order after this file

Read these coordination documents from the same branch:

```text
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/README.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/BASELINE_REVIEW_AND_COMPATIBILITY_NOTES.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/PRODUCER_CAPTURE_CONTRACT.md
docs/vm_tlb/chatgpt_handoff/awma/sim_compat_capture_v1/ACCEPTANCE_REQUIREMENTS.md
```

Also read the accepted previous-stage report and review pack before editing any baseline summary.

---

# 7. Phase A — Establish clean execution state

1. Fetch the coordination branch and accepted baseline branch/commit.
2. Create or switch to the dedicated working branch.
3. Confirm current HEAD, repo cleanliness, host identity and storage visibility.
4. Record a `SOURCE_ANCHORS.md` containing the exact coordination/baseline Git identities used.
5. Do not rewrite or squash prior accepted evidence.

If local Git object/history is incomplete, fetch the exact remote refs needed. Treat ordinary Git-fetch/worktree issues as solve-and-continue engineering problems.

---

# 8. Phase B — Repair baseline control plane from existing evidence

Perform the stale-summary reconciliation described above.

Required output in this stage's review pack:

```text
BASELINE_CONTROL_PLANE_REPAIR.md
```

It must state:

```text
which files were stale;
which accepted evidence superseded them;
what fields/text were updated;
that no C12 simulation was rerun solely for cleanup;
that qualification remains HASH_BOUND_FIXED_WINDOW_10000;
new review-pack SHA256SUMS closure.
```

If any apparently stale statement is not actually contradicted by accepted evidence, do not edit it merely for cosmetic consistency.

---

# 9. Phase C — Freeze `NEW_SIM_BASELINE_V1` consumer identity

Locate the actual accepted build/runtime artifacts and produce a deterministic identity receipt covering, at minimum:

```text
Framework source commit
Core source commit
qualified simulator binary SHA256
compiler/toolchain/build receipt
base simulator config SHA256
VM/TLB overlay/config SHA256
telemetry exporter/analyzer source identity
normalizer/schema identity
fixed-window policy = 10000 cycles
relevant runtime wrapper source identity
```

Create or reuse a stable:

```text
SIM_BASELINE_ID
```

Rules:

- If all semantic fields match the accepted baseline, reuse the existing identity if one already exists.
- If a semantic field differs, do not silently call it `NEW_SIM_BASELINE_V1`; mint a new ID and explain the difference.
- Path-only relocation without byte/semantic changes may be represented as a compatibility view, not a new scientific baseline.

Required review output:

```text
BASELINE_IDENTITY.json
```

---

# 10. Phase D — Harden formal simulation-input admission

The future producer bundle must be accepted only if it is structurally and semantically usable by the simulator.

The consumer contract must require, directly or through the simulator-native grammar, the information necessary to preserve at least:

```text
PC/static instruction identity
opcode
READ / WRITE / ATOMIC semantics
memory space
byte width
warp identity
CTA identity
active mask
lane addresses where the trace grammar requires them
global event/instruction order required by replay
sync/control semantics
kernel/list membership
terminal COMPLETE state
zero drop/overflow
hash closure
```

Do not invent a second competing trace format if the existing Accel-Sim simulator-native format already carries the needed semantics.

Most importantly, formal admission must include a **real traceg parser/grammar smoke**. Checking only that an `.xz` member exists or decompresses to non-empty bytes is insufficient.

Prefer one of:

```text
existing official parser path;
existing simulator parser in a dry-run/syntax-check mode;
a minimal parser that reuses the authoritative grammar and is regression-checked against historical valid traces.
```

Do not create a loose heuristic parser that would accept semantically malformed input.

---

# 11. Phase E — Required fail-closed negative tests

Create automated or reproducible tests for at least:

```text
1. missing sync/control semantics or required control record
2. kernelslist references a missing member
3. manifest/hash mismatch
4. malformed traceg record
5. missing/invalid width or access semantics when required by grammar
6. nonzero drop/overflow receipt
7. partial/non-terminal bundle
8. direct C16WARP1/MREF input presented as simulator input
```

Every case must fail **before** a formal `SIM_INPUT_ID` is issued.

Also test at least one valid historical recovered trace fixture and show that it passes the grammar/parser regression path.

Do not reinterpret a historical fixture as a current-model input; it is only a parser/admission regression fixture.

Required outputs:

```text
CONSUMER_VALIDATOR_CHANGES.md
NEGATIVE_TEST_RESULTS.tsv
HISTORICAL_FIXTURE_REGRESSION.tsv
```

---

# 12. Phase F — Prepare immutable identity/catalog model for future current-model input

Define or harden the schema for:

```text
SIM_INPUT
SIM_BASELINE
SIM_RUN
SIM_EVIDENCE
```

At minimum, future current-model `SIM_INPUT` identity must bind:

```text
producer bundle hash root
trace/list member hashes
producer terminal receipt
model identity + exact revision
input/scenario identity
backend/dtype/runtime identity
phase = Prefill or Decode
target identity / kernel-launch binding
tracer identity/version/build SHA
trace grammar/schema version
address-context/sidecar identity where applicable
```

A future `SIM_RUN` must bind:

```text
SIM_INPUT_ID
SIM_BASELINE_ID
config/overlay identity
runtime command/environment receipt
fixed-window policy
raw output/log hash
normalized telemetry identity
execution status
```

Prepare schemas and tests now, but do **not** create a fake current-model `SIM_INPUT_ID` without producer bytes.

---

# 13. Phase G — Prepare future bounded replay wrapper

Prepare the exact consumer command/wrapper that will be used when the first current-model bundle arrives.

First current-model baseline replay remains:

```text
fixed window = 10000 cycles
```

The wrapper must collect or preserve, when available within the qualified runtime:

```text
simulated cycles/instructions
VM translation counters
TLB hit/miss counters
PTW activity/latency counters
PWC counters
L1/L2/cache counters
memory/DRAM counters
stall/performance counters
termination/boundary status
```

The wrapper must distinguish:

```text
EXPECTED_FIXED_WINDOW_BOUNDARY
NORMAL_COMPLETION
PARSER_ABORT
SIMULATOR_ASSERT_OR_FATAL
EXTERNAL_RUNTIME_FAILURE
```

A fixed-window stop must never be mislabeled as full-ROI completion.

Use a historical fixture only for regression/smoke if useful. Do not rerun a broad historical matrix.

Required output:

```text
RUNTIME_WRAPPER_PREPARATION.md
```

---

# 14. Phase H — Freeze the future first current-model target contract

The intended first formal current-model target is:

```text
model: Qwen2.5-0.5B
model revision: resolve from accepted Native authority; do not retype from memory if a manifest exists
scenario: S2_TEXT
phase: Prefill
target: accepted Attention/Q05_ATTN target identity and launch binding
```

The reason for using this first is operational: it already has accepted Native workload/target authority and is smaller to close than the heavy GEMM target.

For the future producer bundle, exact binding is mandatory for:

```text
model revision
input bytes/tokenization authority
scenario
backend
runtime
dtype
batch/context/sequence properties relevant to identity
phase
target/kernel launch binding
```

Do not retokenize or substitute a nearby workload merely to make the tracer run.

Prepare a machine-readable expected-input template with fields marked `PENDING_PRODUCER` where actual producer hashes are not yet available.

Required output:

```text
EXPECTED_FIRST_CURRENT_MODEL_INPUT.json
```

---

# 15. Phase I — Produce the consumer-ready checkpoint

Because node109 is currently busy, this Goal must not sit in a wait loop.

After all independent preparation passes, create:

```text
CONSUMER_READY_STATE.json
NEXT_ACTIONS_AFTER_109_READY.md
```

`CONSUMER_READY_STATE.json` must contain at least:

```text
status = 174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
SIM_BASELINE_ID
baseline qualification scope
validator/parser identity
negative-test summary
historical-fixture regression result
catalog/schema identity
runtime-wrapper identity
expected first target identity fields
remaining dependency = NODE109_SIM_COMPAT_PRODUCER_BUNDLE
```

`NEXT_ACTIONS_AFTER_109_READY.md` must specify the exact continuation order:

```text
1. independently rehash producer bundle
2. verify producer terminal receipt
3. verify exact workload/target identity
4. run formal admission + real grammar smoke
5. issue stable SIM_INPUT_ID only after PASS
6. preserve raw immutable; derive compatibility view only if necessary
7. run NEW_SIM_BASELINE_V1 10k-cycle replay
8. repeat for determinism
9. normalize telemetry
10. issue SIM_RUN_ID / SIM_EVIDENCE
11. record Native↔Simulation relation only as EXACT_WORKLOAD_TARGET_DIFFERENT_CAPTURE
```

No Native-vs-Simulation numerical calibration is part of this Goal.

---

# 16. Tests and regressions

At minimum run and record:

```text
Git/source anchor checks
baseline identity/hash checks
baseline review-pack SHA closure after repair
consumer validator tests
all required negative tests
valid historical trace fixture grammar/parser test
catalog/schema tests
runtime wrapper smoke/regression where bounded and justified
Foundation or existing relevant repository regression suite
```

Resolve ordinary path/toolchain/test-harness breakage inline.

---

# 17. Required review pack

Create:

```text
docs/vm_tlb/review_packs/AWMA_SIM_CONSUMER_PREP_174NEW_V1/
```

Minimum contents:

```text
README.md
SOURCE_ANCHORS.md
BASELINE_CONTROL_PLANE_REPAIR.md
BASELINE_IDENTITY.json
CONSUMER_VALIDATOR_CHANGES.md
NEGATIVE_TEST_RESULTS.tsv
HISTORICAL_FIXTURE_REGRESSION.tsv
CATALOG_SCHEMA_PREPARATION.md
RUNTIME_WRAPPER_PREPARATION.md
EXPECTED_FIRST_CURRENT_MODEL_INPUT.json
CONSUMER_READY_STATE.json
NEXT_ACTIONS_AFTER_109_READY.md
TEST_AND_REGRESSION_SUMMARY.md
CLAIM_BOUNDARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_CONSUMER_PREP_174NEW_REPORT.md
```

The final report must state one of:

```text
174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1
```

or, only if genuinely blocked:

```text
174NEW_SIM_CONSUMER_PREP_BLOCKED_<EXACT_REASON>
```

---

# 18. Solve-and-continue policy

Do not stop for ordinary recoverable engineering issues such as:

```text
Git fetch/worktree setup
stale helper paths
parser build paths
compiler/library discovery
review-pack formatting
catalog schema formatting
runtime wrapper paths
historical fixture relocation
```

Fix them, regression-test, document, continue.

Stop early only if a genuine semantic contradiction is found in the accepted baseline, the historical valid fixture cannot be parsed by the claimed authoritative grammar after reasonable recovery, or a required artifact is objectively unavailable and cannot be reconstructed from accepted authority.

---

# 19. Forbidden actions / claim boundary

Forbidden:

```text
no node109 GPU work in this Goal
no waiting/polling loop for node109
no C16WARP1/MREF -> traceg synthesis
no fake current-model SIM_INPUT_ID
no current-model simulation without admitted producer bytes
no TLB/Segment/cache mechanism sweep
no full-ROI claim
no historical binary identity claim
no exact historical numerical-equivalence claim
no mutation of accepted Native raw evidence
no destructive cleanup of historical sources
```

Allowed terminal claim after success:

```text
174-new is prepared to admit a future simulator-native current-model bundle
against the hash-bound NEW_SIM_BASELINE_V1 fixed-window consumer contract.
```

Nothing stronger is implied until the future node109 producer bundle is independently admitted and replayed.
