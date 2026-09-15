# Runtime reconstruction

## Attempts

1. Fetched `gpgpu-sim` branch `hrl/vm-core-v0` (`7be87f53...`) and created isolated Framework worktree at historical Framework `d64408a...`. Build command used `make -j2 GPGPUSIM_ROOT=<isolated clone> GPGPUSIM_CONFIG=release ACCELSIM_CONFIG=release`. Result: blocked at `/usr/local/cuda/bin/nvcc: not found` (and `makedepend` could not complete). This is a toolchain blocker, not a source failure.
2. Located executable shared binary `/root/share/workspace_migrated_20260905/results/ep_l2_m1_equivalence/build-m1/accel-sim.out`, SHA `abb81843ed31582beb28dd24f045eb44e26464e2261518a72d21ea511654faa2`. It is not the historical C12 binary SHA `2351f67...` and strings show an EP-L2 build path. It is therefore `REBUILT/OTHER_RUNTIME`, not historical authority.
3. Bounded one-trace parser/simulator anchor with a real shared `.traceg.xz` and a generated one-entry list. VM overlay was rejected by the non-VM binary (`Unknown Option: -gpgpu_vm_mode`). A base-config retry ran for 30 seconds and timed out (`RC=124`) after emitting simulator telemetry. No result reproduction or scientific comparison is claimed.

## Current capability

Historical exact replay remains blocked: exact Core object `57bb71...` is unavailable from fetched remote, historical binary hash is not present, and CUDA `nvcc` is absent. The source-level modern path remains documented in the V1 inventory. A future run needs a compatible CUDA/toolchain or a verified prebuilt VM-enabled binary plus trace/config roots.
