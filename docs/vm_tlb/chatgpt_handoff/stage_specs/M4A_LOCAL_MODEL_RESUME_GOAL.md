# M4A local-model resume -> pilot completion -> formal Goal capture

## Status

**AUTHORIZED NOW once the rented 4xSM86 instance is powered back on.**

This stage replaces the previous Hugging Face credential-only P5 admission path. The user now has a locally stored Llama-3.2-1B snapshot on the main development server and Codex has already produced a local integrity record stating that the required Transformers snapshot is complete and corresponds to the frozen model revision.

The scientific requirement is exact model identity/provenance, not that the rented host itself re-download the gated model from Hugging Face. Therefore a checksum-verified transfer of the already-held exact snapshot from the user's main server to the user's rented GPU node is an approved transport path.

No Hugging Face token is required on the rented node if the local snapshot passes the provenance gates below and the runtime is forced to use that local snapshot without network fallback.

## Frozen model/workload contract

Preserve:

- model identity: `meta-llama/Llama-3.2-1B`;
- immutable research revision: `4e20de362430cd3b72f300e6b0f18e50e7166e08`;
- capture dtype: bfloat16;
- TP=4;
- batch=8;
- input sequence=64;
- output tokens=3;
- rank0-only NVBit tracing;
- separate `prefill` and `decode1` profiler ROIs;
- model load / TP setup / flat-weight rebinding / warmup outside formal ROI;
- NVBit 1.7.6 / reviewed trace format;
- Weight + observable real KV metadata;
- no synthetic KV in capture;
- capture classification remains `PAPER_COMPATIBLE_SELF_CAPTURE`.

Do not change the NVIDIA driver.

## Accepted prior pilot/checkpoint state

The earlier rented-host pilot already established P1-P4 PASS before shutdown:

- approved host: 4 x RTX 3080 Ti, SM86;
- locked Python/PyTorch/CUDA-12.6 environment;
- checksum-verified NVBit 1.7.6 build;
- generic NVBit trace/postprocess/archive chain;
- real four-rank CUDA and rank0-only injection proof.

Pre-shutdown durable checkpoint on the main server:

`/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/`

Remote retained work root before shutdown:

`/root/autodl-tmp/m4a-llama`

Previous Goal status `GOAL_BLOCKED` is historical and may be reopened by this handoff after the new local-model provenance/staging gate passes. Do not require the old pilot to already say PASS before performing the authorized resume gates below.

## Main-server local model source

Candidate local snapshot:

`/workspace/model/meta-llama__Llama-3.2-1B_main`

Existing local records reported by Codex:

- `/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/LOCAL_MODEL_INTEGRITY.md`
- `/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/REMOTE_MODEL_STAGING.md`

These records are inputs, not a substitute for rechecking the actual files before transfer.

The existing report says the snapshot contains a complete Transformers-compatible 1B BF16 checkpoint and that `model.safetensors` matches the official frozen revision's LFS SHA256. Codex must re-verify the exact local files used for staging and record a machine-readable SHA256 manifest.

Do not transfer unnecessary duplicate material such as `original/` or duplicate `*(1)` files unless the staging manifest proves they are required by the Transformers loader.

## R0 — Power-on / retained-host recovery gate

After the user powers the AutoDL instance back on:

1. reconnect using the existing SSH alias/path;
2. verify the instance again exposes exactly four same-model RTX 3080 Ti / SM86 GPUs;
3. verify driver identity has not unexpectedly changed;
4. verify the large data disk and `/root/autodl-tmp/m4a-llama` survived;
5. verify retained CUDA 12.6 toolkit, Route-E venv, NVBit build, Framework checkout and prior pilot logs still exist;
6. record current remote Framework SHA/worktree state;
7. record free disk;
8. verify no stale trace/torchrun process is alive.

Cheap P1-P4 sanity checks are allowed. Do not reinstall working components unless evidence shows the retained state is invalid.

Hardware mismatch is a hard STOP.

## R1 — Local model provenance + minimal staging

On the MAIN server:

1. read `LOCAL_MODEL_INTEGRITY.md` and `REMOTE_MODEL_STAGING.md`;
2. verify the local candidate directory still exists;
3. independently compute/record a SHA256 manifest for every file selected for transfer;
4. verify required Transformers files exist, including model config, safetensors weights/index if applicable, tokenizer/config assets needed by the chosen loader, and generation config where required;
5. preserve the frozen identity/revision in a staging provenance document.

Then transfer only the required snapshot files with resumable `rsync -P` or equivalent to a stable data-disk path such as:

`/root/autodl-tmp/m4a-llama/models/Llama-3.2-1B-frozen/`

On the rented node:

- recompute SHA256 for all staged files;
- require source manifest == destination manifest;
- record total staged size;
- do not consider directory size alone sufficient evidence.

Any checksum mismatch blocks P5.

## R2 — Local-loader transport support

The current workload wrapper uses the HF repo ID. Add the smallest project-local transport-only adaptation needed so it can instead load the verified local snapshot.

Approved interface:

`M4A_MODEL_LOCAL_PATH=/root/autodl-tmp/m4a-llama/models/Llama-3.2-1B-frozen`

Required behavior:

- if `M4A_MODEL_LOCAL_PATH` is set, `AutoModelForCausalLM.from_pretrained()` must load from that local directory;
- force `local_files_only=True` or an equivalent no-network-fallback contract for the local-path route;
- still require `M4A_MODEL_REVISION=4e20de362430cd3b72f300e6b0f18e50e7166e08` as the research provenance identity;
- sidecar/workload manifests must continue to record canonical model ID + frozen revision, and additionally record local snapshot path/provenance/manifest identity;
- do not relabel local filesystem transport as a different model;
- no HF token is required for this local route;
- online HF loading may remain as an alternate transport path, but must not be used silently when `M4A_MODEL_LOCAL_PATH` is set.

If capture artifact digests/locks include a changed wrapper, update the reviewed digest/provenance and rerun the relevant static/self-tests and capture-ready preflight before GPU workload execution.

This local-loader change is an authorized engineering fix because it changes model transport only, not model/workload semantics.

## R3 — Resume pilot P5 with local model, no tracing

Run the exact real TP4 Llama workload using the local snapshot, without NVBit tracing.

Validate at minimum:

- four ranks / four intended GPUs;
- real TP=4 path;
- B8/S64/G3;
- bfloat16;
- local snapshot selected and no network model fallback;
- successful model load;
- flat-weight rebinding on each rank as designed;
- stable weight addresses across later forward;
- finite/sane output/logits;
- Weight sidecar;
- observable real KV events;
- no OOM;
- no model/revision substitution.

PASS reclassifies the prior P5 credential blocker as resolved by verified local-snapshot transport.

## R4 — Finish the diagnostic pilot P6-P8

After R3/P5 PASS, execute the previously required one real `DIAGNOSTIC_PILOT` decode1 trace:

- model/TP/bind/warmup outside active ROI;
- only decode1 profiler ROI traced;
- rank0-only NVBit;
- raw trace retained;
- postprocess;
- kernel classification;
- Weight/KV metadata validation;
- archive + SHA256;
- copy-back to main server;
- source/destination checksum equality;
- frozen parser compatibility smoke.

Update the existing pilot review pack/report. If all pilot requirements are now satisfied, set exactly:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

The diagnostic decode1 trace remains diagnostic and must not be relabeled formal.

## R5 — Immediate Goal activation after pilot PASS

If and only if R3-R4 make the pilot status exactly:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

then continue **immediately in Codex Goal / 目标 mode**, without another human pause, through the formal M4A-C campaign.

Use `M4A_C_GOAL_CAPTURE.md` as the base formal specification, with these explicit overrides:

1. G0 may admit this Goal from the newly repaired pilot PASS produced under this handoff; the earlier historical `GOAL_BLOCKED` does not permanently block admission.
2. Model-access checks in G1 are satisfied by the checksum-verified local snapshot route; a Hugging Face token is not required.
3. Every formal workload command must use the verified `M4A_MODEL_LOCAL_PATH` and must not fall back to network download.
4. Canonical model ID + frozen revision must still appear in all formal manifests.

Formal Goal sequence:

`G0 -> G1 -> G2 FORMAL prefill -> verified archive/copy-back -> G4 FORMAL decode1 -> verified archive/copy-back -> metadata/classification -> parser/simulator compatibility -> M4A-C closeout`.

Use reconnectable long-running sessions (`tmux` or equivalent), progress logs, disk monitoring and resume semantics already defined in the Goal spec.

## Autonomous troubleshooting

Codex should solve ordinary engineering problems and continue when they do not change the frozen research contract. This includes:

- retained-environment path repair;
- rsync/copy-back mechanics;
- local snapshot loader plumbing;
- wrapper/script bugs;
- NVBit build/runtime integration;
- Python package/path issues while retaining pinned versions;
- CUDA 12.6 toolkit path issues;
- tmux/SSH reconnect;
- checksum/manifest/bookkeeping;
- disk reclamation after a verified copy-back.

After source changes, commit/push explicit paths only, sync the reviewed descendant to the rented node, and rerun affected checks.

Never use `git add .` or `git add -A`.

## Hard STOP boundaries

STOP rather than silently changing:

- GPU model/count/SM class;
- NVIDIA driver;
- canonical Llama model identity or frozen revision;
- model parameter contents compared with the verified local snapshot;
- TP=4;
- B8/S64/G3;
- bfloat16;
- rank0-only tracing;
- profiler ROI boundaries;
- NVBit version/fundamental trace format;
- Weight/KV research semantics;
- permanent NCCL keep/drop policy;
- paper exactness labels;
- Core M1-M3 semantics;
- synthetic KV policy;
- workload/trace fidelity solely to make storage/runtime easier.

If the staged snapshot cannot be proven to match the local verified source, STOP rather than downloading/substituting another model.

## Reporting

Continue maintaining:

- `docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`
- `docs/vm_tlb/codex_handoff/m4a/GOAL_PROGRESS.md`
- `docs/vm_tlb/review_packs/M4A_RENTED_HOST_PILOT/`
- `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/`

Add local-model provenance/staging evidence to the relevant pack without committing the multi-GB model itself.

Final formal Goal status must be exactly one:

- `GOAL_PASS_READY_FOR_CHATGPT_REVIEW`
- `GOAL_BLOCKED`

At final closeout push the Track-B branch and STOP. Do not start Segmentation/M4B/M5, and do not shut down/delete the rented instance until user/ChatGPT review.