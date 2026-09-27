#!/usr/bin/env bash
set -eo pipefail
if [[ $# -ne 7 ]]; then
  echo "usage: $0 CONDITION OUTPUT_DIR BINARY CORE CONFIG TRACE_LIST CPU" >&2
  exit 2
fi
condition=$1
output_dir=$2
binary=$3
core=$4
config=$5
trace_list=$6
cpu=$7
trace_config=/root/workspace/accel-sim-framework-c16-e1-oracle-elastic-b16-reuse-canary-174new-v1/docs/vm_tlb/review_packs/C16_E1_ORACLE_ELASTIC_B16_REUSE_PERFORMANCE_CANARY_174NEW_V1/configs/SM89_RTX4080_AWMA_V1.trace.config
[[ ! -e "$output_dir" ]] || { echo "refusing to overwrite $output_dir" >&2; exit 2; }
mkdir -p "$output_dir"
test -x "$binary" && test -s "$trace_list" && test -s "$config" && test -s "$trace_config"
export CUDA_INSTALL_PATH=/root/workspace/c16_cuda_12_4_build
export PATH=/root/workspace/c16_cuda_12_4_build/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export GPGPUSIM_ROOT=$core
unset GPGPUSIM_SETUP_ENVIRONMENT_WAS_RUN
cd "$core"
source setup_environment release >/dev/null
cd "$output_dir"
start_utc=$(date -u +%FT%TZ)
start_ns=$(date +%s%N)
set +e
TIMEFORMAT="real_seconds=%R\nuser_seconds=%U\nsys_seconds=%S"
{ time taskset -c "$cpu" "$binary" -trace "$trace_list" -config "$config" -config "$trace_config" >simulator.stdout 2>simulator.stderr; } 2>host_time.txt
exit_code=$?
set -e
end_ns=$(date +%s%N)
end_utc=$(date -u +%FT%TZ)
terminal=false
grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' simulator.stdout && terminal=true
status=FAIL
[[ $exit_code -eq 0 && $terminal == true ]] && status=PASS
cat > RUN_RECEIPT.json <<EOF
{
  "schema": "C16_GPGPUSIM_HOST_ACCELERATION_PREFIX_RUN_V1",
  "condition": "$condition",
  "status": "$status",
  "exit_code": $exit_code,
  "terminal_exit_detected": $terminal,
  "start_utc": "$start_utc",
  "end_utc": "$end_utc",
  "elapsed_ns": $((end_ns-start_ns)),
  "cpu_affinity": "$cpu",
  "binary_sha256": "$(sha256sum "$binary" | awk '{print $1}')",
  "core_head": "$(git -c safe.directory='*' -C "$core" rev-parse HEAD)",
  "config_sha256": "$(sha256sum "$config" | awk '{print $1}')",
  "trace_config_sha256": "$(sha256sum "$trace_config" | awk '{print $1}')",
  "kernelslist_sha256": "$(sha256sum "$trace_list" | awk '{print $1}')",
  "scientific_authority": false
}
EOF
sha256sum simulator.stdout simulator.stderr host_time.txt RUN_RECEIPT.json > OUTPUT_SHA256SUMS
exit "$exit_code"
