# M4A-C0 — Rented-Host Bring-up and End-to-End Pilot

## Status

**AUTHORIZED NOW.**

The user has rented a qualifying AutoDL host and has already established SSH reachability from the main development server. This stage is the first real-host execution round. It is intentionally narrower than full `M4A_EXTERNAL_CAPTURE`.

The purpose is to exercise the complete expensive-risk chain once on the real host before allowing Codex Goal mode to run the full capture campaign unattended.

## Scope

Execute only the real-host pilot gates below:

`P0 -> P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> P7 -> P8`

The pilot may install/build/run on the rented host and may set `M4A_C_AUTHORIZED=1` **only for the explicitly authorized pilot actions in this file**.

Do **not** run formal C1/C2 prefill/decode capture closeout yet. Any Llama trace captured in this stage is `DIAGNOSTIC_PILOT`, even if it uses the same B8/S64/decode1 workload as the future formal capture.

## Accepted source/package anchors

Track-B repository/branch:

- `swayhrl/accel-sim-framework`
- `hrl/llm-trace-prep-v0`

Reviewed Route-E implementation:

- implementation commit: `524cb20785ec4632b434a0786181ff814ad7eaba`
- provenance/report descendant: `11b4fc33fe3b9e95ad470bccedc306182c5122b5`
- latest ChatGPT rental-boundary descendant before this pilot: `279b585c82bb1ef3e5a4400ad279db9dc96e3571`

The remote checkout used for pilot execution must be this reviewed line or a descendant containing only authorized pilot fixes.

## Remote-execution policy

Codex is authorized to use the already-configured SSH path from the main development server to the rented AutoDL host.

Resolve the SSH target from the existing SSH configuration/session state. Do not print, commit, or copy private keys, passwords, access tokens, or other credentials. If more than one plausible rented host exists and the target cannot be resolved unambiguously, ask only for the SSH alias; do not ask the user to repeat hardware/setup information already discoverable from the host.

Prefer non-interactive SSH commands and resumable scripts/logs. Record exact commands in the review pack, but redact secrets.

## Autonomous-fix authorization

Within this pilot, Codex may diagnose and fix issues without waiting for human review when the fix is local and does not alter the frozen research contract. Authorized autonomous fixes include:

- missing ordinary Linux packages/tools;
- Python/venv/pip setup;
- local CUDA-toolkit installation/path setup;
- build flags/path/provenance bugs;
- shell/Python capture-script defects;
- NVBit build integration defects while retaining the frozen NVBit version and trace format;
- SSH/rsync/copy-back mechanics;
- cache/temp/data-directory placement;
- deterministic runtime bugs in the prepared wrapper that do not change workload semantics;
- diagnostic-only instrumentation/logging needed to identify a failure.

After a concrete fix, rerun the affected gate and all relevant earlier smoke checks.

Codex must STOP rather than silently changing any of the following:

- NVIDIA driver;
- GPU model/count/SM class;
- NVBit version or fundamental trace format;
- model identity/revision;
- TP=4 interpretation;
- B8/S64/G3 formal workload contract;
- rank0-only tracing policy;
- contiguous-weight/metadata semantics in a way that changes the research workload;
- paper exactness labels;
- Core M1–M3 simulator semantics;
- permanent NCCL keep/drop policy.

Credential/gated-model access that cannot be resolved from existing host credentials/environment is a user-action blocker; never log `HF_TOKEN`.

## P0 — Local provenance and remote workspace

On the main development server:

1. verify the Track-B branch and reviewed package provenance;
2. verify the local worktree is clean before source edits;
3. identify the SSH target for the rented host;
4. verify a simple remote shell command succeeds;
5. identify the rented host's large local data mount using `df -hT` rather than assuming a path blindly;
6. choose a remote work root on that large mount, e.g. `<DATA_MOUNT>/m4a-llama`;
7. place a clean Track-B repository checkout on the remote host, preferably through HTTPS clone/fetch or rsync preserving Git provenance if remote GitHub access is unavailable.

All large caches/artifacts must use the large data mount, not the small system disk. Redirect at least HF cache, pip cache, temp files, model cache, capture work root, and large archives accordingly.

## P1 — Host-only preflight

Run the prepared `host_preflight.py` on the rented host.

Require:

- exactly 4 visible GPUs;
- all four same model;
- compute capability 8.6;
- >=12 GiB VRAM each;
- adequate CPU/RAM;
- >=500 GiB free on the selected large data filesystem;
- network reachability needed for approved dependencies;
- correct Framework checkout provenance.

Record full `nvidia-smi`, `nvidia-smi -L`, CPU/RAM, OS/image, filesystem/free space, driver, and checkout SHA.

Hardware mismatch is a hard STOP. Missing ordinary host utilities may be installed and the gate rerun.

## P2 — Locked environment and CUDA 12.6 toolkit

Realize the reviewed environment lock on the rented host.

Required:

- Python 3.10 environment on the large data disk where practical;
- PyTorch 2.6.0 cu126;
- Transformers 4.51.3;
- Accelerate 1.6.0;
- Safetensors 0.5.3;
- huggingface_hub 0.30.2;
- explicit CUDA 12.6 toolkit with `nvcc` and `ptxas` at the selected `--cuda-home`;
- no NVIDIA-driver change.

If CUDA 12.6 toolkit is not already installed, Codex may install a **toolkit-only** local copy. Do not install/replace the driver.

Record compiler paths/versions separately from `torch.version.cuda` and from the AutoDL image's displayed CUDA label.

Verify PyTorch sees exactly four GPUs and records their names/capabilities.

## P3 — NVBit bootstrap and generic end-to-end smoke

Set `M4A_C_AUTHORIZED=1` only in the pilot command environment and run:

1. checksum-verifying NVBit 1.7.6 bootstrap using explicit CUDA 12.6 `--cuda-home`;
2. `capture_ready_preflight.py`;
3. `run_generic_nvbit_smoke.sh`.

Require:

`NVBit injection -> raw trace -> postprocess -> kernelslist.g -> archive -> SHA256 integrity`

all PASS.

Record wall-clock, peak/ending disk use, tracer/postprocessor identity, archive size, and checksums.

Failure blocks all LLM work until fixed or classified as a frozen-contract blocker.

## P4 — Real four-rank/rank0-only injection proof

On the actual 4-GPU host, run a tiny real `torchrun --nproc_per_node=4` diagnostic proving:

- smoke mode: ranks 0–3 have no NVBit injection;
- trace mode: rank 0 alone receives the reviewed `CUDA_INJECTION64_PATH`;
- ranks 1–3 do not inherit it;
- each rank maps to a distinct intended GPU and can execute/synchronize a tiny CUDA operation;
- the proof does not require Llama weights.

Use/reuse the reviewed rank wrapper. A small project-local diagnostic script/test may be added if necessary.

## P5 — Hugging Face access and real TP4 Llama smoke, no tracing

Only after P1–P4 PASS:

1. verify access to `meta-llama/Llama-3.2-1B` at immutable revision `4e20de362430cd3b72f300e6b0f18e50e7166e08` without printing credentials;
2. use the frozen Route-E wrapper in **smoke/no-trace** mode;
3. run the real TP=4 B8/S64/G3 path;
4. validate model load, rank/device mapping, flat-weight binding, stable weight addresses after a later forward, finite/sane outputs, sidecar generation, real KV observations, and no OOM.

The large model/cache files must reside on the data disk.

If `HF_TOKEN` or gated-model authorization is unavailable, finish/report all preceding host/NVBit gates and STOP with the minimal exact user action required. Do not substitute another model.

## P6 — Diagnostic decode1 Llama trace end-to-end

After P5 PASS, execute exactly one real Llama trace pilot using the reviewed `decode1` ROI at the frozen B8/S64/G3/TP4 contract.

This run is labeled:

`DIAGNOSTIC_PILOT`

not formal C2 evidence.

The pilot must exercise the same production chain intended later:

- model load / TP setup / flat-weight setup while tracer inactive;
- profiler-controlled `decode1` ROI only;
- rank0-only NVBit injection;
- raw trace retained;
- postprocess;
- kernel classification (`COMPUTE`, `NCCL_COLLECTIVE`, `MEMCPY`, `UNKNOWN_OTHER`);
- Weight + real KV metadata validation;
- archive/checksum integrity.

Verify from evidence that initialization kernels/copies are absent from the formal ROI list. Inventory NCCL rather than deleting it.

Record:

- wall-clock for smoke, trace, postprocess and archive;
- raw/postprocessed/archive sizes;
- disk usage before/after each phase;
- kernel counts by class;
- metadata counts/coverage where available;
- any warnings/unknowns.

Do not run formal prefill in this pilot.

## P7 — Copy-back and frozen parser compatibility smoke

Copy the pilot bundle and required logs/manifests back to persistent storage on the main development server using rsync/scp or another verified method.

Require source and destination SHA256 match before considering copy-back complete.

On the main server, run the frozen trace parser on the copied pilot trace/list(s). Where cheap, start a minimal simulator compatibility smoke using the existing paper-route parser/config infrastructure.

Do not modify Core M1–M3 semantics merely to accept an incompatible trace.

If NCCL/full-list behavior is ambiguous, preserve both raw/full and compute-only evidence and report it; do not make a permanent paper-exact keep/drop decision here.

## P8 — Pilot closeout

Create/update:

`docs/vm_tlb/review_packs/M4A_RENTED_HOST_PILOT/`

with at least:

- `README.md`;
- `SOURCE_ANCHORS.md`;
- `HOST_ENVIRONMENT.md`;
- `GATE_RESULTS.md`;
- `TRACE_PILOT.md`;
- `COPYBACK_AND_PARSER.md`;
- `VALIDATION_SUMMARY.md`;
- `OPEN_ISSUES.md`;
- `RAW_LOG_INDEX.tsv`.

Update:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

Final status must be exactly one of:

- `PILOT_PASS_READY_FOR_GOAL_CAPTURE`
- `PILOT_BLOCKED`

`PILOT_PASS_READY_FOR_GOAL_CAPTURE` requires P1–P7 PASS, including a real TP4 no-trace smoke, one real rank0-only decode1 diagnostic trace, copy-back checksum verification, and parser compatibility evidence sufficient to proceed.

Commit/push only explicit changed paths; never `git add .` or `git add -A`.

Then STOP for ChatGPT review.

## Next round if PASS

If this pilot passes, ChatGPT will issue a separate handoff authorizing Codex **Goal mode** for the full campaign:

`formal prefill + formal decode1 + metadata + archive/copy-back + parser/simulator validation + M4A-C closeout`

That Goal-mode handoff will explicitly permit autonomous diagnosis/minimal fixes within the same frozen-contract boundaries so the campaign can run continuously without human pauses for ordinary setup/runtime issues.
