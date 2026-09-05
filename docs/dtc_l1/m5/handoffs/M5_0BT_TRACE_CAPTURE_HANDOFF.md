# M5.0BT — Paper-10 Exact Trace Capture and Qualification

Status: **M5_0BT_CAPTURE_PACKAGE_V100_READY — WAITING_FOR_CAPTURE_HOST**

The final offline closure is PASS. V100 capture remains a separately supplied
host action; this handoff neither rents nor starts a host.

## Rental-readiness repairs (T-BLOCKER-01..10)

| blocker | closure |
| --- | --- |
| T01 | Dedicated `build_m5_*_trace_sm70.sh` scripts build CUDA-11.8/sm70 capture binaries; old sm52 hashes are explicitly recovery-only. |
| T02 | Controller separates application stdout/tracer stderr and scans only explicit CUDA/NVBit/tracer fatal signatures. |
| T03 | Explicit checker map includes `2dconv -> conv2d`; static regression invokes all nine PolyBench checkers. |
| T04 | Per-workload immutable CAPTURE_RESULT.json records binary, device, separate ordered invocation/geometry manifest hashes, counts, set hashes and bundle ID; global TSV is regenerated only from archive-backed bundles. |
| T05 | `--tracer-framework-src` must be clean and exactly `0db04452`; tool is built in workflow and NVBit archive/tool/postprocess hashes are frozen. |
| T06 | CUDA runtime probe requires one CUDA-visible logical device 0 and records UUID/model/CC; V100/7.0 is required. |
| T07 | Per-workload WorkloadSpec drives conditional CLI/source/build/checker paths; BICG needs no SpMV tree. Resume separates capture-bundle, archive and transfer states. |
| T08 | BICG-first pilot creates a BICG-bound STORAGE_ADMISSION.json. Any non-BICG capture fails without it; projection includes raw+grouped+archive+headroom and safety factor. |
| T09 | Base/IO/OO named qualification family now explicitly sets cap10240; TSV comparison freezes the common 80-SM/ratio-zero contract. |
| T10 | The old live review is marked superseded; its lower historical snapshot is not an executable instruction. |

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
  --tracer-framework-src <clean Framework checkout at 0db04452...> \
  --nvbit-archive <nvbit-Linux-x86_64-1.8.tar.bz2> \
  --out <absolute/paper10-traces>
```

The controller must run with CUDA 11.8 `nvcc`, exactly one V100 made visible to
the CUDA runtime, and a clean tracer Framework checkout at
`0db04452ec1c47630e4b08002067d82c6811e243`. It builds the NVBit 1.8 tracer
itself, builds dedicated sm70 applications, uses `LD_PRELOAD=<tracer_tool.so>
<exact command>`, and records device UUID/model/CC, source/tool/archive hashes,
raw/grouped/list/stdout/correctness evidence. No DYNAMIC_KERNEL_RANGE/fractional
trace is allowed.

Actual capture layout:

```text
paper10-traces/
  bundles/<workload>/{CAPTURE_RESULT.json,SHA256SUMS,application.stdout,
    tracer.stderr,correctness.log,postprocess.stdout,kernel_*_manifest.json,
    traces/{kernelslist,kernelslist.g,stats.csv,kernel-*.trace,kernel-*.traceg}}
  archives/<workload>.tar.zst and archives/<workload>.archive.json
  transfers/<workload>.transfer.json
  CAPTURE_RESULT_MANIFEST.tsv
```

Do not delete uncompressed data before archive/hash verification.  Do not commit traces, executables, raw logs, or datasets; transfer the archive and compact provenance only.

## Ordered invocation and geometry contract

The pinned tracer source writes stats.csv at tracer_tool.cu lines 878--879 with
kernel mangled name plus grid_dimX/Y/Z and block_dimX/Y/Z. The controller
requires those source-supported columns, derives CTA count as grid X*Y*Z, and
creates separate ordered kernel_invocation_manifest.json and
kernel_geometry_manifest.json files. It validates the ordered kernelslist to
kernelslist.g mapping and every replay-required traceg file; it neither uses
an unordered set nor invents geometry fields absent from tracer output.

## Qualification after capture

On the simulator host, first qualify BICG (pressure case) and GESUMMV (contrasting case), adding SpMV and/or 2DConv if required to cover a materially distinct access pattern.  Under **80 SM/cap 10240**, run PAPER_BASE/IO/OO on the same exact trace per workload.  Require parser/identity success, all modes entering the validated DTC timing pipeline, clean PIB/lower/inflight/ref drains, no fatal/assert/deadlock/duplicate-lower/stale-fill failure, and one identical dynamic trace stream across modes.  Cycle equality to PTX execution-driven or cap-256 results is expressly not required.

Only then close Q1 as `TRACE_FORMAL_PATH_VALID` and make trace-driven the default remaining Paper campaign path.  A workload that fails the trace semantic contract is individually classified and may remain execution-driven; this does not silently revert the campaign.

Next state before a capture host is supplied: **`WAITING_FOR_CAPTURE_HOST`**.
