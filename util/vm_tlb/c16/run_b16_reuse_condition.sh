#!/usr/bin/env bash
set -u

if [[ $# -ne 3 ]]; then
  echo "usage: $0 CONDITION OUTPUT_DIR CONFIG" >&2
  exit 2
fi

condition=$1
output_dir=$2
config=$3
core=/root/workspace/gpgpu-sim-c16-b16-reuse-canary-telemetry-v1
framework=/root/workspace/accel-sim-framework-c16-e1-oracle-elastic-b16-reuse-canary-174new-v1
binary=$framework/gpu-simulator/bin/release/accel-sim.out
trace_list=/root/c16_b16_reuse_window_stage/kernelslist.g
trace_config=$framework/docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1/configs/SM89_RTX4080_AWMA_V1.trace.config

mkdir -p "$output_dir"
test -x "$binary" && test -s "$trace_list" && test -s "$config" && test -s "$trace_config" || exit 3

export CUDA_INSTALL_PATH=/root/workspace/c16_cuda_12_4_build
export PATH=/root/workspace/c16_cuda_12_4_build/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export GPGPUSIM_ROOT=$core
cd "$core" || exit 3
source setup_environment release >/dev/null || exit 3
cd "$framework/gpu-simulator" || exit 3
source setup_environment.sh release >/dev/null || exit 3
cd "$output_dir" || exit 3

start_utc=$(date -u +%FT%TZ)
start_epoch=$(date +%s)
printf '%q ' "$binary" -trace "$trace_list" -config "$config" -config "$trace_config" > COMMAND.txt
printf '\n' >> COMMAND.txt

set +e
/usr/bin/time -v -o TIME.txt "$binary" -trace "$trace_list" -config "$config" \
  -config "$trace_config" > simulator.stdout 2> simulator.stderr
exit_code=$?
set -e

end_utc=$(date -u +%FT%TZ)
end_epoch=$(date +%s)
wall_seconds=$((end_epoch - start_epoch))
terminal=false
if grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' simulator.stdout; then terminal=true; fi
status=FAIL
if [[ $exit_code -eq 0 && $terminal == true ]]; then status=PASS; fi

cat > RUN_RECEIPT.json <<EOF
{
  "schema": "C16_E1_B16_REUSE_RUN_RECEIPT_V1",
  "condition": "$condition",
  "status": "$status",
  "exit_code": $exit_code,
  "terminal_exit_detected": $terminal,
  "start_utc": "$start_utc",
  "end_utc": "$end_utc",
  "wall_seconds": $wall_seconds,
  "core_head": "$(git -C "$core" rev-parse HEAD)",
  "framework_head": "$(git -C "$framework" rev-parse HEAD)",
  "binary_sha256": "$(sha256sum "$binary" | awk '{print $1}')",
  "config_sha256": "$(sha256sum "$config" | awk '{print $1}')",
  "trace_config_sha256": "$(sha256sum "$trace_config" | awk '{print $1}')",
  "kernelslist_sha256": "$(sha256sum "$trace_list" | awk '{print $1}')",
  "run_class": "$( [[ $condition == M1_B16_DIAGNOSTIC ]] && echo DIAGNOSTIC || echo PRIMARY )"
}
EOF
sha256sum simulator.stdout simulator.stderr TIME.txt COMMAND.txt RUN_RECEIPT.json > OUTPUT_SHA256SUMS
exit $exit_code
