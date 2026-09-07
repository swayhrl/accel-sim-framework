#!/usr/bin/env bash
# Non-scientific regression for the immutable FAST64 v2 attempt boundary.
# It never invokes accel-sim: /bin/true exercises normal receipt publication.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runner_source="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
validator="$repo_root/util/dtc_l1/validate_fast64_trace_row.py"
collision_child="$repo_root/util/dtc_l1/fixtures/fast64_receipt_collision_child.sh"
work_root=$(mktemp -d /tmp/fast64-v2-receipt-regression.XXXXXX)
immutable_dir="$work_root/immutable"
immutable_runner="$immutable_dir/run_fast64_trace_v2.sh"

test -x "$runner_source" && test -x "$validator" && test -x "$collision_child"
mkdir -p -- "$immutable_dir"
cp -- "$runner_source" "$immutable_runner"
chmod 555 "$immutable_runner"
runner_sha=$(sha256sum "$immutable_runner" | awk '{print $1}')

run_normal="$work_root/normal"
"$immutable_runner" --simulator /bin/true --config "$runner_source" --trace "$runner_source" \
  --trace-config "$runner_source" --run-dir "$run_normal" \
  --attempt-uuid 11111111-1111-4111-8111-111111111111 \
  --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable_runner" \
  --framework-scientific-config-source-sha test-framework \
  --core-source-head test-core --observer-overlay-sha test-observer \
  --result-classification FAST64_CONTROLLER_REGRESSION

test -f "$run_normal/RUN_START.tsv" && test -f "$run_normal/RUN_TERMINAL.tsv"
test "$(awk -F '\t' '$1 == "simulator_exit_status" { count++; value=$2 } END { if (count == 1) print value; else exit 1 }' "$run_normal/RUN_MANIFEST.tsv")" = 0
test "$(find "$run_normal" -maxdepth 1 -name '.RUN_*.tmp.*' -print -quit)" = ""
test $((8#$(stat -c %a "$run_normal/RUN_START.tsv") & 0222)) -eq 0
test $((8#$(stat -c %a "$run_normal/RUN_TERMINAL.tsv") & 0222)) -eq 0

normal_manifest_sha=$(sha256sum "$run_normal/RUN_MANIFEST.tsv" | awk '{print $1}')
if "$immutable_runner" --simulator /bin/true --config "$runner_source" --trace "$runner_source" \
  --trace-config "$runner_source" --run-dir "$run_normal" \
  --attempt-uuid 22222222-2222-4222-8222-222222222222 \
  --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable_runner" \
  --framework-scientific-config-source-sha test-framework \
  --core-source-head test-core --observer-overlay-sha test-observer \
  --result-classification FAST64_CONTROLLER_REGRESSION \
  >"$work_root/duplicate.out" 2>&1; then
  echo "DUPLICATE_NAMESPACE_UNEXPECTEDLY_ACCEPTED" >&2
  exit 1
fi
test "$(sha256sum "$run_normal/RUN_MANIFEST.tsv" | awk '{print $1}')" = "$normal_manifest_sha"
rg -q 'TARGET_NAMESPACE_EXISTS_OR_CREATE_FAILED' "$work_root/duplicate.out"

# A collision is injected only into the disposable namespace.  The runner must
# reject its terminal receipt publication and the validator must reject the
# resulting attempt before it can be considered a natural terminal result.
run_collision="$work_root/collision"
if FAST64_RECEIPT_COLLISION_DIR="$run_collision" "$immutable_runner" \
  --simulator "$collision_child" --config "$runner_source" --trace "$runner_source" \
  --trace-config "$runner_source" --run-dir "$run_collision" \
  --attempt-uuid 33333333-3333-4333-8333-333333333333 \
  --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable_runner" \
  --framework-scientific-config-source-sha test-framework \
  --core-source-head test-core --observer-overlay-sha test-observer \
  --result-classification FAST64_CONTROLLER_REGRESSION \
  >"$work_root/collision.out" 2>&1; then
  echo "TERMINAL_RECEIPT_COLLISION_UNEXPECTEDLY_ACCEPTED" >&2
  exit 1
fi
test ! -n "$(awk -F '\t' '$1 == "simulator_exit_status" { print; exit }' "$run_collision/RUN_MANIFEST.tsv")"
rg -q 'RECEIPT_DESTINATION_ALREADY_EXISTS' "$work_root/collision.out"
if python3 "$validator" --run-dir "$run_collision" --workload-id NN --mode BASE \
  --config-id FAST64_BASE_A1 --config-file "$runner_source" --core-sha test-core \
  --framework-sha test-framework --payload-manifest "$runner_source" \
  --classification FAST64_CONTROLLER_REGRESSION \
  --output "$work_root/collision.json" --require-immutable-attempt \
  >"$work_root/collision-validator.out" 2>&1; then
  echo "PARTIAL_TERMINAL_ATTEMPT_UNEXPECTEDLY_VALIDATED" >&2
  exit 1
fi
rg -q "'simulator_exit_status' absent in run manifest" "$work_root/collision-validator.out"

printf 'FAST64_V2_RECEIPT_REGRESSION_PASS\twork_root=%s\trunner_sha256=%s\n' \
  "$work_root" "$runner_sha"
