# Architecture and local-agent guide

Accel-Sim wraps GPGPU-Sim. Key shader/cache/L2/DRAM code lives in `gpu-simulator/gpgpu-sim/src/gpgpu-sim`; PTX functional execution lives in `src/cuda-sim`; trace replay is driven by Framework `util/job_launching`. Debug a run from its `justrun.sh`; inspect `gpgpusim.config`, trace config and simulator stderr before changing code. This V1 is packaging infrastructure only: do not change timing, cache, L2, TLB, shader or DRAM behavior.

For updates, transfer Git bundles or patches over removable/offline storage, verify SHA256, then use `git fetch <bundle>` / `git am`. Keep Framework and nested GPGPU-Sim commits separate.
