# SG1 reproduction boundary

The static configuration gate is reproducible without simulation:

```sh
python3 util/dtc_l1/tc80_campaign.py resolve-config \
  --base-config configs/dtc_l1/fast64/FAST64_BASE.config \
  --overlay docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_B16_N_OVERLAY.config \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --output /tmp/SG1_B16_N_RESOLVED_CONFIG.tsv
```

Use the TC80-N overlay in the same command for the 80-KiB control.  The
immutable SG1 runner is the only authorized runtime path; it binds a fresh
UUID attempt to the frozen FAST12 authority and rejects non-NORMAL geometry:

```sh
nice -n 5 python3 util/dtc_l1/sg1_campaign.py run \
  --authority docs/dtc_l1/iscas2027/tc80/TC80_WORKLOAD_AUTHORITY.tsv \
  --workload NN --variant B16-N --runs-root /workspace/wave-a-sg1-runs \
  --base-config configs/dtc_l1/fast64/FAST64_BASE.config \
  --overlay docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_B16_N_OVERLAY.config \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config
```

Run `validate` with the identical authority/workload/variant after a natural
terminal record.  Under the current policy, only the explicitly sequenced
TRICKLE pairs may launch.
