# M5.0BT — Paper-10 Exact Trace Capture and Qualification

Status: **ACTIVE — `WAITING_FOR_EXACT_TRACE_CAPTURE`**

This is the researcher-authorized successor to the obsolete cap-256 natural-terminal wait.  It is a provenance and mechanism-qualification gate, not a hardware-performance experiment.

## Authority and frozen items

- Historical Q1 result: `EXECUTION_DRIVEN_REQUIRED`, solely because no exact provenance-compatible Paper trace existed; it is not a trace-DTC semantic defect.
- Superseding Q1 state: `M5.0BF_Q1_REOPENED_FOR_EXACT_TRACE_RECAPTURE`; `TRACE_CAPTURE_AUTHORIZED`; `TRACE_FORMAL_PATH_QUALIFICATION_PENDING`.
- Q2/Q3 remain PASS/frozen: formal Accel-Sim platform is V100/SM7-style **80 SM**, global DTC lower cap **10240**, researcher scaling **128 credits/SM**.
- `80 SM + cap 256` is `CURRENT_INVALID_SUSPECT`, diagnostic-only.  All historical cap-256 results remain validation/provenance anchors, never formal performance results.
- M5.0BT PASS is mandatory before M5.0C.  It replaces the former requirement that cap-256 execution-driven Paper Base jobs naturally terminate.

## Capture contract

The committed contract is [PAPER10_TRACE_CAPTURE_MANIFEST.tsv](../trace/PAPER10_TRACE_CAPTURE_MANIFEST.tsv).  It freezes source/ref identities, expected executable identity, build, input, checker and format for BICG, ATAX, GEMVER, MVT, SYRK, GESUMMV, SYR2K, SpMV, 2MM and 2DConv.  `CAPTURE_TIME_REQUIRED` fields are deliberately fail-closed: the capture script writes immutable hashes/names into the per-workload evidence, and a missing field invalidates that workload.

On one V100 made visible as device 0, use:

```bash
cd <framework-checkout>
CUDA_VISIBLE_DEVICES=<V100> \
  util/dtc_l1/capture_m5_paper10_traces.sh \
  --polybench-src <polybenchGpu@5584aaa7...> \
  --spmv-wrapper <gpgpu-workloads-spmv-wrapper@de9cf...> \
  --parboil-src <parboil@4e0fc...> \
  --spmv-input-dir <canonical-medium-input-dir> \
  --spmv-reference <canonical-reference.bin> \
  --tracer-so <tracer_tool.so> \
  --postprocess <post-traces-processing> \
  --out <absolute/paper10-traces>
```

The script must run with CUDA 11.8 `nvcc` and an NVBit 1.8 tracer compiled from Framework tracer source at `0db04452ec1c47630e4b08002067d82c6811e243`.  It uses `LD_PRELOAD=<tracer_tool.so> <exact command>`, checks each application, runs `post-traces-processing kernelslist`, requires raw files and `kernelslist.g`, detects tracer fatal/error lines, records `nvidia-smi`, CUDA/toolchain and hashes all raw/grouped/list/stdout/correctness evidence.  No DYNAMIC_KERNEL_RANGE/fractional trace is allowed.

Expected return layout:

```text
paper10-traces/{manifest.tsv,SHA256SUMS,environment.txt}/<workload>/
  {capture.log,correctness.log,kernelslist,kernelslist.g,stats.csv,kernel-*.trace,kernel-*.traceg}
```

Do not delete uncompressed data before archive/hash verification.  Do not commit traces, executables, raw logs, or datasets; transfer the archive and compact provenance only.

## Qualification after capture

On the simulator host, first qualify BICG (pressure case) and GESUMMV (contrasting case), adding SpMV and/or 2DConv if required to cover a materially distinct access pattern.  Under **80 SM/cap 10240**, run PAPER_BASE/IO/OO on the same exact trace per workload.  Require parser/identity success, all modes entering the validated DTC timing pipeline, clean PIB/lower/inflight/ref drains, no fatal/assert/deadlock/duplicate-lower/stale-fill failure, and one identical dynamic trace stream across modes.  Cycle equality to PTX execution-driven or cap-256 results is expressly not required.

Only then close Q1 as `TRACE_FORMAL_PATH_VALID` and make trace-driven the default remaining Paper campaign path.  A workload that fails the trace semantic contract is individually classified and may remain execution-driven; this does not silently revert the campaign.

Next state before a capture returns: **`WAITING_FOR_EXACT_TRACE_CAPTURE`**.
