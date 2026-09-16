# CODEX GOAL — node109 SIM_COMPAT_CAPTURE_V1 Producer Qualification

Run on **node109 / RTX4080** in a fresh worktree/branch.

Suggested branch:

```text
hrl/awma-sim-compat-capture-109-v1
```

## Goal

Build/requalify a simulator-native capture path on RTX4080/SM89 and close the first formal current-model `SIM_COMPAT_CAPTURE_V1` bundle for exact Qwen2.5-0.5B S2_TEXT Prefill Attention.

This is a solve-and-continue Goal. Do not stop at the first tracer build/runtime compatibility issue. Diagnose, make semantics-preserving fixes, regression-test, document, and continue.

## Source authority

Start from this coordination branch and consume:

```text
NEW_SIM_BASELINE authority:
2cbb3bd7c85dd46977c2dbbbe829961c2f03ab49

consumer implementation/contracts:
util/vm_tlb/awma/simulation/
docs/vm_tlb/review_packs/AWMA_NEW_SIM_BASELINE_174NEW_V1/
```

Resolve the latest accepted Qwen0 Native target/input authority from the accepted producer/review manifests. Do not reconstruct the input by prose.

## Phase A — CPU-only producer audit

Before GPU admission:

1. inventory existing Accel-Sim/NVBit tracer code, branches, CUDA assumptions and output grammar;
2. identify the shortest path to native `.traceg.xz + kernelslist.g` production on SM89;
3. compare tracer-required NVBit/CUDA versions with node109's known working NVBit environment;
4. build in user-owned paths; no sudo required;
5. inspect any SM89/driver/API compatibility error to root cause;
6. make narrow compatibility fixes only when simulator semantics remain unchanged;
7. freeze source and binary hashes;
8. prepare exact target manifest and size/disk guards;
9. create local parser/list/hash validation commands before touching the GPU.

Do not fork a new trace grammar unless the existing native tracer is genuinely unsuitable and the alternative is formally lossless.

## Phase B — GPU admission and micro-canary

Use:

```text
/data/c16/locks/c16_gpu_campaign.lock
```

Never bypass or delete an active lock. If another formal capture owns the GPU, continue CPU work or wait for clean admission; do not kill the owner.

With the lock:

1. run a very small CUDA canary;
2. prove tracer injection/load on RTX4080 CC8.9;
3. prove kernelslist + trace payload creation;
4. validate actual traceg grammar/records, not only xz readability;
5. verify required instruction semantics including sync/control;
6. verify COMPLETE / zero drop / zero overflow.

If the tracer uses a different terminal/completeness mechanism than the existing AWMA manifest, write a semantics-preserving adapter receipt; do not invent completion evidence.

## Phase C — Exact Qwen target binding

Bind the accepted exact target:

```text
Qwen2.5-0.5B
exact accepted revision
S2_TEXT
PREFILL
ATTENTION_CORE / Q05_ATTN authority
exact accepted input binding
exact backend/dtype/context
exact launch selector
```

Check model revision and input SHA before every formal attempt.

No retokenization, model substitute, backend fallback, dtype change, or shortened context is allowed for FORMAL evidence.

## Phase D — Target canary and volume qualification

Run the exact workload/target in a bounded diagnostic capture to prove:

- launch selector matches the intended kernel;
- capture starts/stops on the intended target scope;
- estimated trace size is safe;
- target semantics are complete;
- there is enough disk capacity.

If output is too large, explicitly narrow the simulation target/ROI and update TARGET identity/scope. Never silently truncate while preserving the old target identity.

## Phase E — Formal capture

Capture the formal selected target with simulator-native ordering.

Required artifacts:

```text
kernelslist.g
*.traceg.xz
producer manifest
address/context sidecar(s)
terminal/completeness receipt
source/binary/environment receipt
SHA256 manifest
```

Do not MREF-shard or post-hoc concatenate records if doing so loses global instruction/warp order.

## Phase F — Producer-side qualification

Run all available producer checks:

- exact identity re-check;
- kernelslist grammar/list closure;
- trace decompression and actual parser grammar smoke;
- all referenced trace members present;
- semantics coverage check;
- terminal COMPLETE;
- drop/overflow zero;
- repeated hash/read stability;
- source/binary hash closure.

Create READY only after all formal gates pass.

## Phase G — Transfer and producer/consumer handoff

Publish through the accepted 109→174/node164 pipeline. Do not scp ad-hoc into a consumer raw directory and bypass receipts.

Producer report must contain the exact ready path/run ID, payload SHA set and intended `WORKLOAD_ID/TARGET_ID` relation so 174-new can independently admit it.

## Optional extension

Only after the Prefill Attention formal bundle is fully closed, a second target may be attempted if bounded and useful. Prefer an already-accepted Decode attention/KV target over heavy GEMM if the Decode target identity is already formally closed. Otherwise STOP after first target.

## Required review pack

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_CAPTURE_109_V1/
```

Minimum files:

```text
README.md
EXECUTION_CONTEXT.md
TRACER_SOURCE_AND_BUILD_RECEIPT.md
SM89_COMPATIBILITY_CHANGES.md
MICRO_CANARY_RESULT.md
FORMAL_TARGET_BINDING.json
TARGET_VOLUME_QUALIFICATION.md
SIM_COMPAT_CAPTURE_MANIFEST.json
TRACE_MEMBER_MANIFEST.tsv
TERMINAL_AND_COMPLETENESS.md
TRANSFER_RECEIPT.md
TEST_AND_REGRESSION_SUMMARY.md
CLAIM_BOUNDARY.md
OPEN_ISSUES.md
SHA256SUMS
```

Codex report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_CAPTURE_109_REPORT.md
```

## STOP condition

Preferred:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
```

STOP with a non-PASS only after bounded recovery genuinely proves the required simulator semantics cannot be preserved on node109 with the available tracer/toolchain, or an external resource cannot be safely obtained. State the exact blocker.

Do not start simulator mechanism experiments. Do not modify Native evidence or its scientific status.
