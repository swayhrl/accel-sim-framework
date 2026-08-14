# Decoupled-L2 follow-up CUDA trace queue

This is the persistent intake queue for suites that are present in the
Accel-Sim application ecosystem but are not contained in the public V100
pretrace archives used by the current experiment campaign.  It records the
workload selection before trace generation, so a missing trace can never be
mistaken for a completed simulator result.

The source baseline is the sibling checkout
`/workspace/worktrees/gpu-app-collection-decoupled-l2` at commit
`dad09cb0487845edc7524ded814c6cde9f0ef6a1`.  It is intentionally outside the
Accel-Sim worktree; this experiment branch only owns the queue and replay
configuration.

## Selected cases

`experiments/decoupled_l2_followup_trace_queue.csv` queues nine cases:

- DeepBench NVIDIA normal GEMM plus Tensor-Core GEMM, convolution, and RNN.
  These cover the DNN/GEMM/Tensor-Core mix exposed by the native
  `Deepbench_nvidia_normal` and `Deepbench_nvidia_tencore` definitions.
- CUDA sample `cudaTensorCoreGemm`.
- CUDA SHOC Level-1 `Spmv`, `Stencil2D`, `Triad`, and `FFT`.  The CUDA tree is
  selected deliberately; the neighbouring OpenCL SHOC tree is not useful to
  the NVBit/Accel-Sim SASS trace flow.

## State transition

The four DeepBench rows are `public_archive_available`; the official V100 1.1.0
FTP catalog provides `deepbench.tgz` (55 GiB compressed, approximately 1.2
TiB uncompressed).  The FTP directory exposes the complete gzip archive only,
not per-workload trace objects.  With the current 70 GiB free-space budget and
a required 20 GiB reserve, it cannot be staged locally yet.  The remaining
five rows start in `trace_needed`.  A trace collection run must:

1. build the selected CUDA program from the pinned application checkout;
2. collect its SASS trace with the standard Accel-Sim/NVBit flow, retaining
   the resulting `kernelslist.g` and all referenced `kernel-*.traceg` files;
3. replace `PENDING` with the trace-root-relative directory (the directory
   containing `traces/`) and record collection provenance; and
4. copy the five replay fields into a normal pretrace manifest, then run
   `scripts/run_decoupled_l2_pretrace_cases.sh` for a paired baseline and
   decoupled replay.

The counter gate is intentionally the same minimum L2 activity gate used by
the existing application manifests.  It is a replay gate, not a claim that
the still-uncollected trace has been tested.

The public V100 archive catalog was checked on 2026-08-14.  It provides
DeepBench but no separate CUDA Tensor-Core GEMM or SHOC archive.  Therefore
the queue does not guess a trace name or start an invalid replay.  Once
enough disk is explicitly released for DeepBench, archive staging must still
select and record the exact member paths before paired replay.

## AccelWattch artifact intake

Zenodo record 5398781 provides a separate AccelWattch artifact containing a
cudaTensorCoreGemm validation SASS trace.  Its direct content endpoint is:

```text
https://zenodo.org/api/records/5398781/files/accelwattch-artifact-appendix.tar/content
```

The 2026-08-14 record metadata specifies `39660062720` bytes and MD5
`c66259f73a622228bbcf02a4ef4f9b6a`.  The local resumable download is kept at
`hw_run/decoupled-l2-pretraces/accelwattch-artifact-appendix.tar`; do not
extract it until this exact size and digest have passed.  Member selection
will be recorded before staging any trace, so the archive cannot be confused
with a completed cudaTensorCoreGemm replay.
