# AI-trace / NVBit server bootstrap

Use this runbook before any Lane G model or scientific capture. It is a
qualification sequence, not an installation script: never upgrade CUDA,
driver, PyTorch, or NVBit from this path.

## Retry570 known matrix

`NVBIT_LANE_G_RTX3090_CUDA124_KNOWN_GOOD.json` pins the observed working
minimal path: RTX3090/SM86, driver 570.124.04, CUDA 12.4, PyTorch 2.5.1+cu124,
and NVBit 1.7.5 with EAGER module loading. NVBit 1.8 is known bad only for the
same Lane G PyTorch first-use path: its core stalls in module bookkeeping even
though an official tiny smoke can pass. Do not generalize either result beyond
that matrix.

## New-server sequence

1. Fetch the Lane G commit and the pinned runtime profile.
2. Materialize the exact NVBit archive/core/tool; verify every SHA256.
3. Invoke `retry570_nvbit175_preflight.py` with both the absolute `--nvdisasm`
   and absolute `--nsys` executable. It verifies actual GPU/driver,
   CUDA tools, child `PATH`, `NVDISASM`, PyTorch/libtorch, tool identity,
   existing smoke receipts, stale processes, and measurement marker state.
4. Run native PyTorch, official NVBit, exact EMPTY, then original Lane G
   first-kernel no-trace smokes in that order if any corresponding receipt is
   absent. A later step cannot repair an earlier failure.
5. Run the Q0 prewarm gate outside `MEASUREMENT_ACTIVE`. Verify zero trace
   files before declaring `LANE_G_RUNTIME_READY`.
6. Only then run the two independent Q1 deterministic capture canaries.

## Child environment contract

The login shell is not evidence. Each injected child must receive an explicit
environment containing the profile's CUDA `bin` directory in `PATH`,
`NVDISASM=nvdisasm`, and `CUDA_MODULE_LOADING=EAGER`. Record the resulting
child environment in every receipt.

## Measurement hygiene

```
process -> NVBit/CUDA init -> prewarm -> READY -> trace count zero
        -> MEASUREMENT_ACTIVE -> CAPTURE_BEGIN -> one target -> CAPTURE_END
        -> remove marker -> parse/hash/cleanup
```

Prewarm is never timing evidence. A prewarm trace, stale marker, stale GPU
process, timeout, or forced kill fails closed. The external parent process owns
the timeout and process-group cleanup; a child must not be its own watchdog.

## Stop conditions

Until a Q1/Q2 publication is reviewed, do not run a full model, Llama, Qwen,
C frozen target, broad capture, 300-second watch, or historical 6+6 rerun.
If the profile differs, report `UNVALIDATED_MATRIX`; do not silently substitute
tools or broaden the workload.
