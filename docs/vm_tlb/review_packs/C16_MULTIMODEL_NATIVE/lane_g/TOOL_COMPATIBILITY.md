# C16 Lane G tool compatibility expectations

This is an offline expectation matrix, not a claim that the current local host or an AutoDL instance has these capabilities. C16-1.1 records the actual GPU/driver/CUDA values before a scientific run.

| Tool | Required C16 behavior | Offline state | Runtime gate |
| --- | --- | --- | --- |
| `nsys` | CUDA/NVTX lightweight census; capture-range bounded to NVTX | wrapper dry-run passed | G1 checks launch/stream/name/correlation/NVTX linkage and measures overhead |
| `ncu` | query and freeze a compact available metric list; one target only | wrapper dry-run passed | G2 records `COUNTER_UNAVAILABLE` rather than substituting a similar counter |
| NVBit launcher/tool | target-in/out filter, terminal trace, identity closure, 4 GiB/20 min guard | wrapper dry-run passed | G3 tiny CUDA fixture then one revalidated model target |
| PyTorch/HF/AutoAWQ | local-files-only model import with exact dtype/quantization | CPython 3.10 offline wheel/install/import closure | G0 rejects CPU/dtype/backend fallback; GPU runtime remains required |
| execution-budget ledger | shared 24 GPU-instance-hour wall-time / 64 GiB raw accounting, serialized capture lease | ledger unit test passed | C16-1.1 initializes it; every real runner/profiler command requires it |

No wrapper uses `ncu --set full`; no wrapper requests full SASS; no wrapper invokes Accel-Sim or GPGPU-Sim.
