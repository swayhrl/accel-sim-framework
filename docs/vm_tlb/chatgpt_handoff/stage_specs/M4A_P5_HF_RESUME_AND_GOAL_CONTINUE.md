# M4A P5 — Hugging Face Credential Resume and Conditional Goal Continuation

## Status

**AUTHORIZED NOW, conditional on a user-provisioned valid Hugging Face credential.**

The rented-host pilot reached a narrow user-action blocker after P1–P4 passed. The host, locked Python/CUDA environment, NVBit bootstrap/generic trace chain, and real four-rank rank0-only injection diagnostic are accepted pilot evidence. The pilot stopped before Llama because no usable Hugging Face credential was available on the rented host.

This stage authorizes resuming the existing pilot at P5. If P5–P8 then pass and the pilot status becomes exactly `PILOT_PASS_READY_FOR_GOAL_CAPTURE`, Codex may immediately continue in **Goal / 目标 mode** into the already prepared full M4A-C formal capture goal without another human pause.

## Frozen host / environment evidence already accepted

Rented host pilot evidence records:

- 4 × NVIDIA GeForce RTX 3080 Ti, 12 GiB each, SM86;
- driver 595.71.05, unchanged;
- large work root `/root/autodl-tmp/m4a-llama`;
- Python 3.10.12;
- PyTorch 2.6.0+cu126, `torch.version.cuda == 12.6`;
- Transformers 4.51.3;
- Accelerate 1.6.0;
- Safetensors 0.5.3;
- huggingface_hub 0.30.2;
- selected CUDA toolkit `/root/autodl-tmp/m4a-llama/cuda-12.6`;
- NVBit 1.7.6 checksum/build/generic smoke PASS;
- pilot P4 real four-rank CUDA/rank0-only injection proof PASS.

Do not redo P1–P4 unless a later change or failure invalidates them. A cheap sanity recheck of GPU count, disk, environment and tracer is allowed before P5.

## Credential policy

The Hugging Face token is a user secret. It must never be:

- committed to Git;
- pasted into Codex/chat logs;
- printed by scripts;
- placed on a command line visible to process listings when avoidable;
- copied into review-pack raw logs.

A credential may be provided by either:

1. a normal Hugging Face cached login available to `huggingface_hub`; or
2. a user-created local secret file on the rented host with mode 0600, loaded into `HF_TOKEN` only inside the relevant remote process environment.

A cached authenticated token is considered equivalent to an `HF_TOKEN` environment variable for admission. Do **not** block merely because `env | grep HF_TOKEN` is empty if `huggingface_hub` can securely resolve a valid cached token.

If using a secret file, the recommended location is:

`/root/autodl-tmp/m4a-llama/secrets/hf_token`

with parent directory and file protected by `umask 077` / mode 0600. Never print its contents.

Codex may add minimal credential-loader plumbing to the capture wrapper if needed, provided it only selects between `HF_TOKEN` and the normal Hugging Face cached credential and does not change workload/model semantics.

## P5-R — Credential and exact model-access proof

Before downloading weights, verify access to exactly:

- repo: `meta-llama/Llama-3.2-1B`
- immutable revision: `4e20de362430cd3b72f300e6b0f18e50e7166e08`

Use `huggingface_hub` with the resolved token and fetch only a small metadata/config file first.

Required evidence:

- authenticated identity can be resolved without printing the token;
- exact revision resolves;
- a tiny file such as `config.json` downloads successfully;
- the resolved commit/revision matches the frozen SHA;
- no alternate model/revision is substituted.

If the credential is syntactically valid but the account lacks gated-model permission, STOP with the exact user action required (request/approve Llama access). Do not substitute another model.

## Resume original pilot P5–P8

After P5-R PASS, resume the existing `M4A_C0_RENTED_HOST_PILOT.md` at P5:

- real TP=4 B8/S64/G3 Llama smoke without tracing;
- flat-weight binding and stability proof;
- real Weight/KV sidecar evidence;
- one `DIAGNOSTIC_PILOT` decode1 rank0-only NVBit trace;
- postprocess/classification/archive/checksum;
- copy-back with source/destination checksum equality;
- frozen parser compatibility smoke;
- pilot review-pack/report closeout.

Do not relabel the pilot decode1 trace as formal.

Pilot final status remains exactly one:

- `PILOT_PASS_READY_FOR_GOAL_CAPTURE`
- `PILOT_BLOCKED`

## Conditional Goal activation

If and only if the pilot becomes:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

then **without waiting for another human review**, remain/switch into Codex **Goal / 目标 mode** and continue the full formal goal defined by:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_C_GOAL_CAPTURE.md`

and the start override:

`docs/vm_tlb/chatgpt_handoff/M4A_GOAL_MODE_START.md`

Execute the formal goal continuously through its internal gates:

`G0 -> G1 -> G2 formal prefill -> G3 verified copy-back -> G4 formal decode1 -> G5 verified copy-back -> G6 metadata/classification -> G7 parser/simulator compatibility -> G8 closeout`.

Use the next several hours productively. Do not pause at ordinary PASS gates.

## Autonomous troubleshooting remains authorized

For ordinary environment/build/download/SSH/tmux/rsync/wrapper/runtime problems, diagnose root cause, implement the minimal safe fix, rerun affected checks, and continue.

Hard STOP rather than silently changing:

- NVIDIA driver;
- GPU model/count/SM class;
- Llama model/revision;
- TP=4;
- B8/S64/G3;
- bfloat16 self-capture choice;
- rank0-only tracing;
- profiler ROI boundaries;
- NVBit version / fundamental trace format;
- Weight/KV object semantics;
- permanent NCCL keep/drop policy;
- paper exactness labels;
- Core M1–M3 simulator semantics;
- synthetic-KV policy.

## Credential lifetime

Keep the credential available only as long as needed for the active rental campaign. Never include it in archives/copy-back/review packs. If a protected credential file is used, it may remain on the rented host during the campaign so reconnectable Goal-mode jobs can authenticate; remove it after the user confirms the campaign is complete.

## Reporting

Continue maintaining:

- `docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`
- `docs/vm_tlb/codex_handoff/m4a/GOAL_PROGRESS.md` once formal Goal mode activates
- pilot and external-capture review packs as defined by their stage specs.

After formal Goal closeout, push explicit paths only and STOP for ChatGPT review. Do not start Segmentation/M4B/M5.