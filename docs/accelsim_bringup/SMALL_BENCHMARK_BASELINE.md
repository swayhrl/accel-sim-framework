# Small Benchmark Baseline

`scripts/accelsim/a8_small_benchmark_baseline.sh` wraps the A7B N-app runner to produce a bounded baseline CSV.

Defaults:

```bash
ACCELSIM_A8_MAX_APPS=5
ACCELSIM_A8_TIMEOUT_SEC=900
ACCELSIM_A8_INCLUDE_MICRO=1
ACCELSIM_A8_DRY_RUN=0
```

The baseline uses traces that already exist locally. It does not download traces, build benchmark apps, or run a full benchmark suite.

A8 is baseline-quality only if the latest A7A clean baseline report is `PASS`. If A7A did not pass, A8 can still run for debugging but reports `PARTIAL_PASS_NOT_BASELINE_QUALITY`.

Outputs:

- `.local_reports/A8_small_benchmark_baseline_*.md`
- `.local_reports/A8_small_benchmark_baseline_*_stats.csv`
- `.local_logs/A8_small_benchmark_baseline_*.log`

The CSV mirrors A7B per-app columns and can be used as a small infrastructure sanity baseline before later paper reproduction work.
