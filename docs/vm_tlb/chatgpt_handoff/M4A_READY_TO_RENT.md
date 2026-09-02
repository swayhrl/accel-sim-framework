# Track B — READY TO RENT / host-preflight-only next step

This file is the current Track-B authorization and overrides stale pre-rental wording in older `CODEX_NEXT_STAGE.md` snapshots.

## Reviewed status

`M4A_PRERENTAL_REVIEW_FIX`: **PASS / READY_TO_RENT**.

Accepted Route-E implementation commit:
`524cb20785ec4632b434a0786181ff814ad7eaba`

Final provenance/report descendant:
`11b4fc33fe3b9e95ad470bccedc306182c5122b5`

The user may now rent one qualifying Route-E host: four same-model SM86 GPUs on one physical host, all four allocated in one instance. RTX 3080 Ti 12 GiB is accepted; RTX 3090 is optional headroom. Require >=500 GiB free/expandable local data storage, sufficient host RAM, SSH/copy-back, and revalidate all hardware after rental.

## M4A-C remains gated

Formal capture is still **NOT AUTHORIZED**.

After rental, execute only the host-suitability gate first; do not set `M4A_C_AUTHORIZED=1`, download Llama weights, or build/capture yet.

Command shape:

```bash
python3 util/llm_trace_capture/host_preflight.py \
  --framework-root "$PWD" \
  --work-root <LARGE_LOCAL_DATA_MOUNT>/m4a-llama \
  --required-gpu-count 4 \
  --minimum-free-gib 500
```

Use the actual large local-data mount, not a small system partition.

After host-preflight:

- PASS -> report/send `host-preflight.json` and STOP for ChatGPT M4A-C authorization;
- BLOCKED -> report exact reason and STOP.

Prefer a host/image with an explicit CUDA 12.6 toolkit already available at a known path. The rental page's CUDA 13.x label is not the project toolchain. If CUDA 12.6 is unavailable, stop after host preflight and resolve the approved local toolkit path before any NVBit build; never change the NVIDIA driver.

Future M4A-C after a new authorization: isolated pinned Python/PyTorch environment -> explicit CUDA-12.6 toolkit -> checksum NVBit bootstrap -> generic tracer smoke -> capture-ready preflight -> real TP4 smoke/flat-buffer/VA checks -> tiny LLM ROI trace/disk projection -> formal prefill/decode1 -> archive/copy-back -> parser/simulator compatibility.
