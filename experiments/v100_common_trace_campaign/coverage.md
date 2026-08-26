# V100 common memory-stream capture coverage

The trace format is the standard Accel-Sim/NVBit SASS format.  Each
`kernel-*.traceg.xz` records dynamic instructions and their memory operands;
the generated `kernelslist.g` preserves the replay order.  It is therefore a
memory-access stream, not merely a kernel-launch log.

The following common SHOC workloads were already captured by the completed
TLS/C2P campaign with the same SHOC revision, V100, CUDA 11.8, and
`-s 1 -n 1 -d 0` input policy.  They are deliberately reused instead of
re-traced:

| Workload | Reusable archive |
|---|---|
| FFT | `hw_run/tls-c2p-v100-20260822/archives/tls-shoc-fft.tar.zst` |
| Stencil2D | `hw_run/tls-c2p-v100-20260822/archives/tls-shoc-stencil2d.tar.zst` |

The accompanying manifest contains the three remaining GPU-only common cases:
SHOC Spmv, SHOC Triad, and CUDA `cudaTensorCoreGemm`.  The DeepBench cases in
the older follow-up queue are not GPU-capture gaps: they are available only as
a 55 GiB official V100 archive (about 1.2 TiB expanded), so staging it on the
current 241 GiB AutoDL disk is intentionally deferred.
