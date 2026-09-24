# Code map delta

- `src/gpgpu-sim/oracle_elastic_residency.{h,cc}`: canonical sidecar parser, internal SHA-256, interval lookup, exact quota distributor, victim policy and diagnostic schema.
- `src/gpgpu-sim/gpu-cache.h`: per-line protected/pending/class metadata, centralized opt-in config and per-instance accounting state.
- `src/gpgpu-sim/gpu-cache.cc`: actual `mem_fetch::get_addr()`/`GLOBAL_ACC_R` target gate, enabled-only victim path, fill-time protection commit, pending reservation bound, invalidation/flush accounting and diagnostic output.
- `src/gpgpu-sim/gpu-sim.{h,cc}`: centralized option registration and post-topology oracle initialization.
- `src/gpgpu-sim/l2cache.cc`: passes the real memory-subpartition identity only when the feature is enabled; OFF retains the baseline `-1` tag-array identity.
- `src/gpgpu-sim/tests/`: policy, parser/SHA, quota, synthetic behavior, line/sector metadata and actual tag-array configuration tests.
- `docs/c16/oracle_elastic_qweight_residency_v1/`: schema, implementation boundary, synthetic sidecar and B8/B16/B24/BFULL overlays.

No observation-only telemetry class is used as functional replacement state.
