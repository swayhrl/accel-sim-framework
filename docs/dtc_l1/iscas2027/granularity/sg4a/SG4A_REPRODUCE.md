# SG4A static gate and immutable execution boundary

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
and the workspace filesystem had inadequate headroom).  After a later
resource-gated admission, SG4A.2 launched twelve immutable UUID attempts for
GESUMMV and BICG at logical 32/64/80 KiB in IO and OO mode; their live status
is recorded in `SG4A_STAGE_STATUS.tsv`.  They remain unaccepted until natural
exit and `sg4a_campaign.py validate` strict PASS.

`SG4A_FAST12_MISSING_POINT_PLAN.tsv` is the hash-locked 72-cell remaining/full
FAST12 matrix, and `validate_sg4a_fast12_plan.py` checks it without a
simulator.  Any later launch must use a fresh UUID namespace and respect the
resource gate, with GESUMMV, BICG, and ATAX first.  Do not replace the frozen
16-KiB reference or alter any frozen FAST64 evidence.
