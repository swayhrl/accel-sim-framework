# CODEX 109 — C16 Formal Campaign V2 Recovery and Capture Goal

Execution node: 109 / RTX4080
Mode: GOAL MODE, multi-hour, unattended
Base scientific failure evidence: `3eb1087c710a796797074dca66b1c96228d6fd45`

## Goal

Recover from the V1 all-MREF tracer failure and produce high-quality formal C16 trace evidence. Solve recoverable engineering problems inside this goal rather than stopping at the first blocked matrix row.

This goal includes:

1. all-MREF capture architecture recovery;
2. Qwen0 formal trace capture;
3. AWQ `awq_ext` recovery and fused-backend capture when possible;
4. raw Qwen2.5-7B S2 memory recovery;
5. `CAPTURE_CAMPAIGN_V2.tsv` construction and execution;
6. Pipeline V1 publication/ACK for accepted formal bundles.

## Read first

```text
RECOVERY_MASTER_PLAN_V2.md
TRACE_CAPTURE_ARCHITECTURE_V2.md
RAW7B_MEMORY_RECOVERY_V2.md
AWQ_EXTENSION_RECOVERY_V2.md
CAMPAIGN_MATRIX_V2_RULES.md
```

Also read the V1 formal campaign review pack and the frozen precapture review pack.

## Branch isolation

Use a fresh worktree/branch. Suggested:

```text
hrl/c16-formal-trace-campaign-109-v2
```

Do not rewrite V1 review evidence.

## GPU serialization

Before each GPU run, ensure no conflicting C16 or unrelated compute process is using the RTX4080. Use the existing shared campaign lock if present. Do not kill unrelated users/processes without authorization.

## Phase A — reproduce the V1 blocker briefly

Do not spend another hour rediscovering it.

Use the known Qwen0 S2 attention target and static index 4110 control to verify:

```text
single-MREF control PASS
all-MREF complete-launch failure still reproducible
```

Then immediately move to the V2 sharding experiments.

## Phase B — find a terminal-close all-MREF shard size

For the exact target launch:

1. all GLOBAL MREF + CTA0;
2. CTA0..1;
3. geometric CTA scaling;
4. record event count/bytes/time/terminal status.

If CTA0 all-MREF passes, CTA sharding is the primary formal method.

If CTA0 all-MREF fails, partition static MREFs and qualify MREF-sharded capture.

If both remain too slow, implement the compact binary warp-event path described in the architecture document.

Do not use a single MREF as the final scientific representation.

## Phase C — implement formal shard bundle metadata

Every shard/group must carry machine-readable metadata with:

```text
source target identity
model/input/scenario
launch selector
code object SHA
static MREF set SHA
CTA/MREF shard selector
tracer build commit/SHA
record format version
event/drop/overflow/terminal counters
supported analyses
unsupported claims
```

The parent logical target must have a manifest listing all child shard RUN_IDs and merge semantics.

## Phase D — Qwen0 formal targets

Capture in priority order:

1. S2 Prefill Attention;
2. S2 Prefill heavy GEMM;
3. Decode early memory target;
4. Decode late KV/Attention target when available.

For each target:

```text
identity canary
bounded shard canary
immediate fingerprint sanity check
formal shards
audit completeness
Pipeline finalize/publish/ACK
```

At least Attention + heavy GEMM should be attempted to formal acceptance before moving on solely because one target is difficult.

## Phase E — AWQ extension recovery

Follow `AWQ_EXTENSION_RECOVERY_V2.md`.

Do not destructively replace the active environment. Build/test extension in isolation first.

If `awq_ext` succeeds:

- create a new fused deployment identity;
- re-run bounded NSYS census;
- generate RTX4080-local static maps;
- build object map;
- capture at least one fused quantized GEMM/dequant or attention target with the qualified V2 trace method.

If `awq_ext` is ABI-blocked after serious source-build attempts:

- preserve evidence;
- optionally create a separately named Triton AWQ deployment if installable without damaging the base environment;
- otherwise retain unfused AutoAWQ as a control only;
- continue Qwen0/raw7B work.

## Phase F — raw Qwen2.5-7B memory recovery

Follow the exact ladder in `RAW7B_MEMORY_RECOVERY_V2.md`.

Required attempts before final `TRUE_CAPACITY` defer:

1. clean exact reproduction with memory telemetry;
2. expandable-segments fresh process;
3. confirm lazy module loading and warmup policy;
4. inspect/use official last-token-logit control when supported and prove target-kernel equivalence;
5. reduce capture-tool memory overhead with V2 sharding;
6. if needed, test the Prefill-equivalent harness under its strict equivalence criteria.

Do not CPU-offload model layers/KV as a formal workaround.

If admitted, prioritize a raw7B Prefill Attention/GEMM target; Decode is optional if capacity remains tight.

## Phase G — campaign matrix V2

Create and continuously update:

```text
docs/vm_tlb/review_packs/C16_FORMAL_TRACE_CAMPAIGN_109_V2/CAPTURE_CAMPAIGN_V2.tsv
```

Do not let a recoverable state remain as the final explanation. Resolve it to formal/control/defer/reject by the end.

## Pipeline V1

Use the accepted integration implementation, including the SSHFS content-copy semantics and one-writer admission rule.

Every formal raw/shard must be locally hash-closed before transfer. Pipeline ACK is required before `FORMAL_ACCEPTED`.

Transport failure never authorizes GPU rerun when the local bundle is intact.

## Analysis compatibility

Until 174-new explicitly supports V2 shard merging, also produce small derived shard summaries locally:

```text
unique 4K pages
unique 64K pages
unique 128B lines
object mix
load/store/atomic mix
CTA identity
```

These are sanity checks, not a replacement for raw.

## Time management

Do not spend the entire goal on one engineering path.

Suggested effort ceilings before switching recovery strategy:

```text
V1 reproduction: <=15 min
CTA sharding qualification: <=45 min
MREF sharding qualification: <=45 min
compact tracer implementation/qualification: <=90 min
AWQ extension recovery: <=90 min before classifying ABI-blocked
raw7B memory recovery: <=60 min before scoped Prefill/defer decision
```

These are prioritization guides, not hard failure timers. Continue longer when clear progress is being made.

## Required review pack

```text
docs/vm_tlb/review_packs/C16_FORMAL_TRACE_CAMPAIGN_109_V2/
```

At minimum:

```text
README.md
FINAL_DECISION.json
CAPTURE_CAMPAIGN_V2.tsv
TRACE_METHOD_QUALIFICATION.tsv
SHARD_MANIFEST_INDEX.tsv
FORMAL_TRACE_INDEX.tsv
PIPELINE_ACK_INDEX.tsv
RAW7B_MEMORY_RECOVERY.tsv
AWQ_EXTENSION_RECOVERY.tsv
AWQ_BACKEND_IDENTITY.json
OBJECT_MAP_INDEX.tsv
STATIC_MAP_INDEX.tsv
CANARY_QUALITY.tsv
FAILURE_AND_RECOVERY_LOG.tsv
RAW_LOG_INDEX.tsv
OPEN_ISSUES.md
SHA256SUMS
```

## Acceptance

### Campaign PASS

Require:

- at least one Qwen0 high-value target formal-accepted through Pipeline V1;
- no single-PC target promoted as representative evidence;
- formal evidence class and unsupported claims explicitly recorded;
- raw/shard hashes and target identities closed;
- analysis sanity fingerprint nontrivial and internally consistent.

Strong target:

- Qwen0 Prefill Attention + heavy GEMM accepted;
- plus one Decode or AWQ/raw7B target accepted.

### Acceptable partial

`FORMAL_CAMPAIGN_V2_PARTIAL_WITH_ROOT_CAUSE` is allowed if Qwen0 formal data exists but secondary deployments remain deferred with strong evidence.

### Global failure

`FORMAL_CAMPAIGN_V2_FAIL_GLOBAL_BLOCKER` only when all exact useful capture paths fail, including CTA sharding, MREF sharding, and compact-record recovery, or when infrastructure/authority is globally unavailable.

## STOP boundary

Do not stop for intermediate approval.

STOP only after:

- the campaign reaches a final decision;
- all formal local bundles have been published/ACKed when possible;
- review pack is hash-closed;
- execution branch is committed and pushed;
- worktree is clean.
