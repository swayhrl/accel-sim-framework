# SG4A static gate and deferred execution boundary

The following commands reproduce the completed static gate without starting a
simulator:

```sh
python3 util/dtc_l1/tc80_campaign.py resolve-config \
  --base-config configs/dtc_l1/fast64/FAST64_IO.config \
  --overlay docs/dtc_l1/iscas2027/granularity/sg4a/config/SG4A_LOGICAL80_IO_OVERLAY.config \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --output /tmp/SG4A_LOGICAL80_IO_RESOLVED_CONFIG.tsv
python3 util/dtc_l1/validate_sg4a_static.py \
  --repo . --core-repo /workspace/repos/gpgpu-sim_distribution
```

At the recorded bootstrap the contract barred new simulators (swap was nonzero
and the workspace filesystem had inadequate headroom).  SG4A.2 therefore has
no attempt UUIDs and must not be represented as executed.  When admission is
truthfully restored, launch missing 32/64/80-KiB FAST12 rows in immutable UUID
namespaces, with GESUMMV, BICG, and ATAX first.  Do not replace the frozen
16-KiB reference or alter any frozen FAST64 evidence.
