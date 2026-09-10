#!/usr/bin/env bash
# Read-only parser regression; the fixture is synthetic and never a result.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
fixture="$repo/util/dtc_l1/testdata/fast64_3_2d_base_diagnostic_v1.stdout"
tmp=$(mktemp -d /tmp/fast64-3-2d-diagnostic-v1-XXXXXX)
trap 'rm -rf -- "$tmp"' EXIT

python3 "$repo/util/dtc_l1/analyze_fast64_3_2d_base_diagnostic_v1.py" \
  --input "$fixture" --output "$tmp/result.json"
python3 - "$tmp/result.json" <<'PY'
import json
import pathlib
import sys

result = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert result["schema"] == "FAST64_3_2DCONVOLUTION_BASE_DIAGNOSTIC_V1"
assert result["classification"] == "NONFORMAL_DIAGNOSTIC_NOT_RESULT"
assert result["deadlock_cores"] == [3, 29]
owner_line = result["l1d"]["L1D_3"]["reserved_lines"][0]
absent_line = result["l1d"]["L1D_29"]["reserved_lines"][0]
assert owner_line["owner_state"] == "OWNER_PRESENT"
assert owner_line["owner"]["request_uid"] == 77
assert owner_line["owner"]["pending_read"] == 2
assert absent_line["owner_state"] == "OWNER_ABSENT"
assert result["l1d"]["L1D_3"]["owners_with_pending_children"][0]["request_uid"] == 77
PY
printf 'FAST64_3_2D_BASE_DIAGNOSTIC_V1_REGRESSION_PASS\n'
