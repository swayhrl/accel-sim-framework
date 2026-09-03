# Current state — Track B

## Accepted capture state

Track-B Route-E LLM data acquisition is **PASS / FROZEN** after post-capture review.

Accepted/prepared stages:

- `M4A_PRECAPTURE_PREP`: PASS;
- `M4A_PRECAPTURE_FIXUP`: PASS;
- `M4A_PRERENTAL_FINALIZE`: PASS after review-fix;
- `M4A_PRERENTAL_REVIEW_FIX`: PASS;
- rented-host pilot / real TP4 validation: PASS for capture admission;
- `M4A_C_FORMAL_CAPTURE`: PASS;
- post-capture archive/evidence audit: `POSTCAPTURE_REVIEW_PASS_SAFE_TO_POWER_OFF`.

The rented GPU host is no longer required. No recapture is authorized.

## Frozen formal artifacts

Capture executable Framework:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Model:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Workload/capture contract:

- one physical 4xSM86 host during capture;
- real TP=4;
- rank0-only NVBit injection;
- BF16;
- batch 8;
- input sequence 64;
- generation 3;
- distinct profiler-controlled prefill and first-decode (`decode1`) ROIs;
- raw/full rank0 ROI trace retained intact;
- one contiguous rank-local Weight allocation plus runtime-observed real KV events;
- no synthetic KV;
- fidelity label: `PAPER_COMPATIBLE_SELF_CAPTURE`, not author-exact.

Formal prefill:

- run `m4a-llama-prefill-20260902T182016Z`;
- 724 raw traces / 724 traceg traces;
- archive `/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`;
- SHA256 `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`.

Formal decode1:

- run `m4a-llama-decode1-20260903T004138Z`;
- 772 raw traces / 772 traceg traces;
- archive `/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`;
- SHA256 `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`.

Both main-server archives have independently verified outer SHA256, zstd/tar integrity and internal `SHA256SUMS`. Raw/traceg data, sidecars, manifests, logs and provenance are retained.

Frozen parser compatibility anchor used by capture closeout:

`73774727e25fadf89df6f30ef5cf014091115db7`

This old Core is only a trace-format/parser compatibility anchor. Future integration must use the final accepted Track-A M1–M3 Core.

## Independent review findings before integration

Two post-capture analysis issues do **not** invalidate capture, but must be repaired before A/B integration:

### Semantic kernel classification

The formal `kernelslist.g` entries are trace filenames. Actual semantic CUDA kernel names live inside each trace header (`-kernel name = ...`). The existing filename-only classifier therefore incorrectly reports embedded NCCL kernels as COMPUTE. The current old compute-only derivative is not a valid semantic compute-only partition list.

Raw/full capture evidence remains valid and immutable. No permanent NCCL keep/drop decision has been made.

### Address/object coverage

The existing coverage analyzer is not accepted for formal quantitative use because it does not decode all tracer address encodings/all active-lane references. The tracer uses list-all, base-stride and base-delta warp-address formats. Formal Weight/KV coverage therefore remains `UNKNOWN` until corrected offline streaming analysis completes.

KV matching must also respect ROI timing: prefill must not classify future decode-step ranges as active prefill KV; decode1 may conservatively use the observed prefill state plus the immediate decode1 result, but not future decode2/3 ranges.

## Current authorization

Execute only:

`M4A_MERGE_PREP`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_MERGE_PREP.md`

Start override:

`docs/vm_tlb/chatgpt_handoff/M4A_MERGE_PREP_START.md`

Run as one continuous internal target:

`MP0 -> MP1 -> MP2 -> MP3 -> MP4 -> MP5 -> MP6 -> MP7 -> MP8`.

After PASS, STOP for ChatGPT review before any Track-A merge or M4B work.

## Merge boundary

Track A is currently independently finishing M1–M3 VM baseline closeout on `hrl/vm-m1-m3-v0`.

Do **not** merge while Track A is running.

Future intended integration, only after both sides independently PASS:

- create a new integration branch (planned class: `hrl/vm-llm-m4b-v0`);
- Core source comes from final accepted Track-A M1–M3;
- carry Track-B LLM/capture utilities, immutable artifact provenance and reviewed M4A evidence into the integration branch;
- rewrite unified `CURRENT_STATE.md` / `CODEX_NEXT_STAGE.md` rather than choosing stale A/B versions mechanically;
- first integration gate is LLM replay/translation characterization before Segmentation.

## Explicit exclusions

Track B must not currently:

- access/rent a GPU or recapture data;
- modify either formal archive;
- modify Track-A branch or Core;
- merge A and B;
- implement Segmentation or L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/migration/UVM/MCM;
- choose a permanent NCCL keep/drop policy;
- claim runtime-range matching is exact per-instruction tensor lifetime attribution.
