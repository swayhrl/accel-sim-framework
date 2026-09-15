# SG1 reproduction boundary

The static configuration gate is reproducible without simulation:

```sh
python3 util/dtc_l1/tc80_campaign.py resolve-config \
  --base-config configs/dtc_l1/fast64/FAST64_BASE.config \
  --overlay docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_B16_N_OVERLAY.config \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --output /tmp/SG1_B16_N_RESOLVED_CONFIG.tsv
```

Use the TC80-N overlay in the same command for the 80-KiB control. Runtime
experiments are not launched until the Wave-A host resource gate records zero
swap and all contract admission conditions.
