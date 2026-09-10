#!/usr/bin/env bash
# Read-only regression against the already terminal DWT2D precompute.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run=/workspace/fast64-runs/fast64_3_precomputed_dwt2d_base_cap8192_a1_r2
summary="$repo/docs/dtc_l1/fast64/generated/fast64_3_dwt2d_base_alias_v3/fast64_3_precomputed_dwt2d_base_cap8192_a1_r2.json"
perf=$(find "$run" -maxdepth 1 -type f -name 'perf_counter_*.csv.gz' | sort | head -1)

python3 - "$repo" "$summary" "$perf" <<'PY'
import json
import pathlib
import subprocess
import sys
import tempfile

repo, summary, perf = map(pathlib.Path, sys.argv[1:])
with tempfile.TemporaryDirectory(prefix="fast64-3-base-structural-v1-") as tmp:
    output = pathlib.Path(tmp) / "result.json"
    subprocess.run(
        [str(repo / "util/dtc_l1/extract_fast64_3_base_structural_metrics_v1.py"),
         "--summary", str(summary), "--perf", str(perf), "--output", str(output)],
        check=True,
    )
    result = json.loads(output.read_text())
assert result["classification"] == "PRECOMPUTED_STRUCTURAL_METRIC_COMPANION_NOT_FAST64_3_PASS"
assert result["metrics"]["cacheline_all_lines_reserved_events"] > 0
assert result["metrics"]["mshr_entry_full_events"] > 0
assert result["metrics"]["mshr_merge_full_events"] == 0
assert result["metrics"]["pib_full_events"] > 0
assert result["metrics"]["live_miss_lower_acquired"] == result["metrics"]["live_miss_lower_released"]
PY
printf 'FAST64_3_BASE_STRUCTURAL_METRICS_V1_REGRESSION_PASS\n'
