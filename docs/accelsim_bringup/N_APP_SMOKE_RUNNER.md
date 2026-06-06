# N-App Smoke Runner

`scripts/accelsim/a7b_n_app_smoke.sh` runs a bounded number of trace apps directly through `accel-sim.out`.

It exists to validate that more than one trace app can run without launching a full benchmark campaign.

The runner:

- discovers `kernelslist.g` files from `ACCELSIM_TRACE_ROOT`, recent reports, `.local_traces`, or `hw_run`;
- selects up to `ACCELSIM_A7B_MAX_APPS` apps;
- creates isolated directories under `.local_runs/`;
- writes per-app logs under `.local_logs/`;
- writes a CSV under `.local_reports/`.

Default knobs:

```bash
ACCELSIM_A7B_MAX_APPS=3
ACCELSIM_A7B_TIMEOUT_SEC=600
ACCELSIM_A7B_DRY_RUN=0
ACCELSIM_A7B_CONFIG_DIR=SM7_QV100
```

Dry run:

```bash
ACCELSIM_A7B_DRY_RUN=1 bash scripts/accelsim/a7b_n_app_smoke.sh
```

Real run:

```bash
bash scripts/accelsim/a7b_n_app_smoke.sh
```

This is a smoke test, not a full Rodinia run.
