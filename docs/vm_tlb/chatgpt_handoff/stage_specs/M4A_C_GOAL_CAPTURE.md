# M4A-C Goal Mode — Full Formal Capture Campaign

## Status

**CONDITIONALLY PRE-AUTHORIZED.**

This stage becomes active only if the immediately preceding rented-host pilot closes with exactly:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

If the pilot closes `PILOT_BLOCKED`, this Goal MUST NOT start. Fix/resolve the blocker first under a new handoff.

Once the pilot PASS condition is met, the user explicitly authorizes Codex **Goal / 目标 mode** to execute the full formal Route-E capture campaign continuously for the next several hours without human pauses between successful internal gates.

The Goal is:

`M4A_C_FORMAL_CAPTURE -> COPYBACK -> PARSER/SIM_COMPAT -> M4A_C_CLOSEOUT`

This Goal does not authorize Segmentation, synthetic KV injection, M4B/M5 performance experiments, or Core M1-M3 semantic changes.

## Frozen research contract

Preserve all of the following throughout the Goal:

- one physical host with 4 same-model SM86 GPUs;
- actual TP=4 execution;
- only rank 0 receives NVBit injection;
- model: `meta-llama/Llama-3.2-1B`;
- immutable revision: `4e20de362430cd3b72f300e6b0f18e50e7166e08`;
- workload: batch=8, input sequence=64, output tokens=3;
- capture dtype: bfloat16, explicitly a self-capture choice;
- separate `prefill` and `decode1` formal ROIs;
- model load / TP setup / flat-weight binding / warmup remain outside the formal ROI;
- NVBit 1.7.6 and the reviewed trace format;
- raw rank0 ROI traces retained intact;
- `COMPUTE`, `NCCL_COLLECTIVE`, `MEMCPY`, `UNKNOWN_OTHER` classification is diagnostic/provenance only;
- no permanent paper-exact NCCL keep/drop policy in this stage;
- Weight + real KV metadata are collected where observable;
- no synthetic KV records are generated;
- capture classification remains `PAPER_COMPATIBLE_SELF_CAPTURE`, never author-exact.

Do not change the NVIDIA driver.

## Source and pilot admission gate — G0

Before any formal run:

1. fetch/pull the latest Track-B branch;
2. read the pilot `LATEST_REPORT.md` and review pack;
3. require final pilot status `PILOT_PASS_READY_FOR_GOAL_CAPTURE`;
4. record the pilot closeout Framework SHA as the Goal starting source anchor;
5. ensure both local and rented-host checkouts are clean or contain only explicitly documented runtime artifacts outside Git;
6. confirm the rented instance is still the same approved 4xSM86 host;
7. confirm the remote large data filesystem remains available;
8. confirm no pilot fix changed any frozen research contract above.

If any admission item fails, set Goal `BLOCKED` and STOP.

The Goal may reuse the pilot's already-installed environment, downloaded model, CUDA 12.6 toolkit, NVBit build, and verified caches. Do not reinstall working components merely for cleanliness.

## Goal progress / recovery state

Maintain:

`docs/vm_tlb/codex_handoff/m4a/GOAL_PROGRESS.md`

After every gate record:

- gate ID;
- status `NOT_STARTED | RUNNING | PASS | FAIL | BLOCKED`;
- local Framework SHA;
- remote Framework SHA;
- remote host identity summary;
- exact command/run ID;
- wall-clock;
- disk before/after;
- artifact/archive/checksum paths;
- copy-back destination;
- unresolved warnings;
- next gate.

This file is the resume point after SSH/session interruption.

A completed, source/destination-checksum-verified formal bundle must not be recaptured merely because a later gate fails.

## Long-running remote execution policy

Formal NVBit traces may legitimately run for hours. Do not classify a run as hung from wall-clock alone.

Run long remote jobs in a reconnectable session, preferably `tmux`, or an equivalent durable mechanism with PID/log/status files.

While a formal trace is running, poll approximately every 10-15 minutes and record:

- remote process alive/status;
- GPU process/utilization where meaningful;
- trace/log file growth;
- data-disk free space;
- obvious fatal diagnostics.

Do not launch a duplicate formal trace while the original process remains alive.

Treat a run as potentially stuck only if there is no meaningful process activity and no output/trace growth for a sustained interval (normally >=20 minutes), then diagnose before deciding to restart.

If SSH disconnects, reconnect and inspect the durable session/process/logs; do not assume the run failed.

## Autonomous diagnosis / repair authority

Within this Goal, Codex should solve ordinary engineering problems autonomously and continue. Do not stop for issues that can be repaired without changing the frozen research contract.

Authorized autonomous fixes include:

- missing ordinary Linux packages;
- Python/venv/package-path issues while retaining locked versions;
- CUDA 12.6 toolkit path/compiler selection issues;
- build flags and NVBit integration defects while retaining NVBit 1.7.6 and trace semantics;
- verified archive staging from the main server when the rental host cannot reach GitHub;
- resumable HTTP/download/cache placement problems;
- SSH/tmux/rsync/scp/copy-back mechanics;
- shell/Python wrapper defects;
- bookkeeping/checksum/manifest issues;
- log/progress instrumentation;
- deterministic runtime defects that do not change model/workload/TP/ROI/metadata semantics.

After a source/script fix:

1. commit and push it with explicit paths only;
2. synchronize the reviewed descendant to the rented host;
3. rerun the directly affected pilot/smoke checks;
4. rerun `capture_ready_preflight.py` when any locked capture artifact changes;
5. only then resume the formal gate.

Do not use `git add .` or `git add -A`.

## Hard STOP / human-review boundaries

STOP rather than silently changing any of:

- GPU model/count or SM class;
- NVIDIA driver;
- model identity or immutable revision;
- TP=4 interpretation or world size;
- B8/S64/G3 workload contract;
- bfloat16 capture choice;
- rank0-only tracing policy;
- profiler ROI boundaries;
- NVBit version or fundamental trace format;
- Weight/KV object semantics;
- permanent NCCL keep/drop policy;
- paper exactness classification;
- Core M1-M3 simulator semantics;
- use of synthetic KV;
- reduction of workload/trace fidelity merely to make a run fit.

Missing/invalid Hugging Face gated-model credentials are also a user-action STOP. Never print or commit `HF_TOKEN`.

## Disk-safety policy

Use the pilot measurements to project formal capture storage.

Before each formal ROI:

- record current free space;
- estimate peak trace + postprocess + archive footprint;
- preserve a safety reserve; target at least 100 GiB free after projected peak where practical.

If both formal bundles cannot coexist remotely, this is acceptable:

`formal prefill -> archive -> copy back -> verify destination SHA256 -> reclaim verified prefill intermediates -> formal decode1`

Remote deletion is allowed only after:

1. archive integrity test PASS;
2. source SHA256 recorded;
3. destination copy completes;
4. destination SHA256 exactly matches;
5. manifest/review record identifies what was removed.

Prefer deleting regenerable raw/intermediate files rather than the sole remote copy of a validated archive. Never delete the only verified copy.

If even one ROI cannot safely fit by itself, STOP for storage expansion; do not shrink the formal workload or silently filter trace content.

## G1 — Formal entry recheck

Reuse pilot environment, then rerun a compact formal admission set:

- exactly 4 same-model SM86 GPUs visible;
- `capture_ready_preflight.py` PASS with explicit CUDA 12.6 home;
- PyTorch sees four GPUs;
- exact model revision accessible/cached;
- reviewed rank0-only injection diagnostic still PASS if capture scripts changed after pilot;
- generic NVBit smoke only if tracer/bootstrap/capture stack changed after pilot;
- free-disk projection recorded.

Do not redownload/rebuild expensive inputs unnecessarily when checksums prove reuse is valid.

PASS -> G2.

## G2 — Formal prefill capture

Run one formal Route-E prefill capture using the reviewed production driver/wrapper.

Formal identity:

- status: `FORMAL`;
- trace region: `prefill`;
- TP=4;
- B8/S64/G3;
- rank0-only NVBit;
- bfloat16;
- exact frozen model revision.

Required chain:

`no-trace smoke -> TP/load/bind/warmup -> profiler-controlled prefill ROI -> raw rank0 trace -> postprocess -> kernelslist.g -> classification -> Weight/KV metadata validation -> SHA256 manifest -> archive -> archive integrity test`

Record at minimum:

- unique run ID;
- start/end UTC times;
- total wall-clock;
- trace wall-clock;
- postprocess wall-clock;
- archive wall-clock;
- raw trace size;
- postprocessed trace size;
- archive size;
- disk before/peak/after where measurable;
- kernel count by class;
- Weight metadata summary;
- KV metadata summary;
- model/rank/output sanity;
- warnings/unknowns.

Hard assertions:

- initialization/model-load kernels and ROI-inactive initialization HtoD copies are absent from the formal ROI list;
- raw formal list is preserved;
- NCCL records are classified, not destructively removed;
- no `SYNTHETIC_KV` exists.

PASS -> G3.

## G3 — Prefill immediate copy-back and checkpoint

Copy the completed prefill bundle to persistent storage on the main development server.

Require:

- archive exists and integrity test PASS on remote;
- remote source SHA256 recorded;
- destination archive exists;
- destination SHA256 exactly matches source;
- destination path recorded in Goal progress and review pack.

After this PASS, the prefill bundle is a durable checkpoint. If disk pressure warrants, reclaim remote prefill intermediates according to the disk-safety policy.

PASS -> G4.

## G4 — Formal decode1 capture

Run a fresh formal `decode1` capture, distinct from the pilot diagnostic run.

Use exactly the same frozen model/workload/TP/dtype/rank0 policy.

Initialization and required prefill execute with formal tracing inactive; only the first decode operation is in the profiler-controlled ROI.

Run the same complete chain and record the same provenance/size/timing/kernel/metadata fields as G2.

The pilot decode trace may be used only for expected-behavior comparison; it must not be relabeled as this formal run.

PASS -> G5.

## G5 — Decode1 copy-back and checkpoint

Perform the same archive/integrity/source-destination SHA256 procedure as G3.

At completion, require two independent persistent formal bundles on the main server:

- prefill;
- decode1.

Do not shut down/delete the rented host yet.

PASS -> G6.

## G6 — Formal metadata and kernel-manifest validation

For both formal bundles validate and summarize:

- exact model/revision/workload provenance;
- rank0 flat Weight base/size and tensor offsets;
- known Weight trace-address coverage;
- real KV addresses/ranges/events where observable;
- KV reuse/growth/replacement/lifetime events available from the sidecar;
- no unjustified overlapping live object ranges;
- `UNKNOWN` remains `UNKNOWN` rather than guessed;
- no synthetic KV;
- raw/full kernel list identity;
- class counts for COMPUTE/NCCL/MEMCPY/UNKNOWN;
- compute-only derivative identity;
- raw file/checksum preservation.

If metadata coverage is partial but internally correct, quantify the gap and preserve it for review. Do not fabricate classification coverage.

PASS -> G7.

## G7 — Main-server parser / simulator compatibility

On the main development server, using the copied formal data:

For each formal ROI, test where applicable:

1. raw/full kernels list through the frozen parser;
2. compute-only derived list through the same parser;
3. minimal existing paper-route simulator/config smoke where practical.

Record:

- parser command/status;
- unsupported opcodes/kernels if any;
- NCCL-specific failures if any;
- ISA/config identity;
- whether the trace addresses overlap expected Weight/KV sidecar ranges;
- simulator startup/completion result for minimal smoke.

Do not modify Core M1-M3 to force acceptance.

A raw/full-list parser failure caused only by retained NCCL may coexist with a successful compute-only parse and still allow this Goal to complete for human policy review, provided:

- the raw formal trace remains intact;
- the failure is precisely attributed;
- the compute-only derivative is reproducible;
- no permanent paper-exact keep/drop decision is claimed.

Any deeper ISA/trace-format incompatibility affecting ordinary compute kernels is `BLOCKED` and must be reported.

PASS or explicit NCCL-policy-only review state -> G8.

## G8 — M4A-C Goal closeout

Create/update:

`docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/`

with at least:

- `README.md`;
- `SOURCE_ANCHORS.md`;
- `HOST_ENVIRONMENT.md`;
- `GOAL_GATE_RESULTS.md`;
- `FORMAL_PREFILL.md`;
- `FORMAL_DECODE1.md`;
- `METADATA_VALIDATION.md`;
- `KERNEL_MANIFESTS.md`;
- `COPYBACK_CHECKSUMS.md`;
- `PARSER_SIM_COMPAT.md`;
- `VALIDATION_SUMMARY.md`;
- `OPEN_ISSUES.md`;
- `RAW_LOG_INDEX.tsv`.

Update:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

and finalize:

`docs/vm_tlb/codex_handoff/m4a/GOAL_PROGRESS.md`

Final Goal status must be exactly one of:

- `GOAL_PASS_READY_FOR_CHATGPT_REVIEW`
- `GOAL_BLOCKED`

`GOAL_PASS_READY_FOR_CHATGPT_REVIEW` requires:

- valid pilot admission;
- formal prefill captured and copied back with matching SHA256;
- fresh formal decode1 captured and copied back with matching SHA256;
- both archives integrity-tested;
- Weight/KV metadata validated to the available evidence level;
- raw/full and compute-only kernel artifacts retained/reproducible;
- parser compatibility established for normal compute path, with any NCCL-only ambiguity explicitly isolated;
- no frozen research-contract violation;
- source/report provenance pushed and worktrees clean.

This status means the data-acquisition Goal is complete and ready for human review. It does not authorize M4B/M5.

After commit/push, STOP.

Do not shut down/delete the rented instance; leave it intact until the user/ChatGPT reviews copy-back and explicitly releases it.
