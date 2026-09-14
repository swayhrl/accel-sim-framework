#!/usr/bin/env bash
# One-shot NCU N1 hardware-counter canary.  All artifacts are outside Git.
set -euo pipefail
umask 077

usage() {
  echo "usage: $0 --run" >&2
}

[[ $# -eq 1 && $1 == --run ]] || { usage; exit 2; }
[[ $(id -u) -eq 1004 && $(id -un) == huangrulin ]] || {
  echo "FAIL_POLICY: must run as huangrulin UID 1004" >&2
  exit 2
}
[[ $EUID -ne 0 ]] || { echo "FAIL_POLICY: root is forbidden" >&2; exit 2; }
[[ -z ${CUDA_INJECTION64_PATH:-} && -z ${LD_PRELOAD:-} ]] || {
  echo "FAIL_POLICY: NVBit/CUDA injection or LD_PRELOAD is forbidden" >&2
  exit 2
}

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
source_file="$repo/util/vm_tlb/c16/host_4080/ncu_n1_vector_add.cu"
metric_file="$repo/util/vm_tlb/c16/host_4080/ncu_n1_metrics.txt"
nvcc=/usr/local/cuda-12.8/bin/nvcc
ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
raw_root=/data/c16/ncu
canary_root="$raw_root/canary"
expected_uuid=GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59
expected_driver=580.178.04
expected_cuda=/usr/local/cuda-12.8
metric=$(<"$metric_file")

[[ -x $nvcc && -x $ncu && -f $source_file && -f $metric_file ]] || {
  echo "FAIL_PREREQUISITE: fixed executable or source missing" >&2
  exit 2
}
[[ $(readlink -f /usr/local/cuda) == "$expected_cuda" ]] || {
  echo "FAIL_PREREQUISITE: CUDA symlink drift" >&2
  exit 2
}
[[ $(id -nG) != *" docker "* && " $(id -nG) " != *" docker "* ]] || {
  echo "FAIL_POLICY: docker group is forbidden" >&2
  exit 2
}
[[ " $(id -nG) " != *" sudo "* ]] || {
  echo "FAIL_POLICY: sudo group is forbidden" >&2
  exit 2
}
grep -q '^RmProfilingAdminOnly: 0$' /proc/driver/nvidia/params || {
  echo "FAIL_NCU_PERMISSION: loaded profiling permission is not unrestricted" >&2
  exit 2
}
capsh --print | grep -q '^Current: =$' || {
  echo "FAIL_POLICY: effective capabilities are not empty" >&2
  exit 2
}

gpu_line=$(nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader)
[[ $(wc -l <<<"$gpu_line") -eq 1 && $gpu_line == *"$expected_uuid"* && $gpu_line == *"$expected_driver"* ]] || {
  echo "FAIL_PREREQUISITE: unexpected GPU identity: $gpu_line" >&2
  exit 2
}

stamp=$(date -u +%Y%m%dT%H%M%SZ)
run_dir="$canary_root/C16_NCU_N1_$stamp"
report_base="$raw_root/C16_NCU_N1_vector_add_$stamp"
report="$report_base.ncu-rep"
[[ ! -e $run_dir && ! -e $report ]] || { echo "FAIL_OUTPUT_COLLISION" >&2; exit 2; }
mkdir -p "$run_dir"
binary="$run_dir/c16_ncu_vector_add"

printf '%s\n' "$metric" >"$run_dir/metric.txt"
[[ $metric == sm__cycles_elapsed.avg ]] || {
  echo "FAIL_METRIC_FREEZE: unexpected metric-file content" >&2
  exit 2
}
printf '%s\n' \
  'metric_query_command=/opt/nvidia/nsight-compute/2025.1.1/ncu --query-metrics --devices 0 --query-metrics-mode suffix --metrics sm__cycles_elapsed' \
  'metric_query_observation=AD103 output listed sm__cycles_elapsed.avg as Counter with unit cycle' \
  'metric_query_status=FROZEN_FROM_PRE_PROFILE_READ_ONLY_QUERY' \
  >"$run_dir/metric_freeze.txt"

nvcc_argv=("$nvcc" -std=c++17 -O2 -arch=sm_89 "$source_file" -o "$binary")
printf '%q ' "${nvcc_argv[@]}" >"$run_dir/nvcc_argv.txt"; printf '\n' >>"$run_dir/nvcc_argv.txt"
"${nvcc_argv[@]}" >"$run_dir/nvcc_stdout_stderr.txt" 2>&1

native_argv=("$binary")
printf '%q ' "${native_argv[@]}" >"$run_dir/native_argv.txt"; printf '\n' >>"$run_dir/native_argv.txt"
timeout --foreground 30s "${native_argv[@]}" >"$run_dir/native_output.txt" 2>&1
grep -q '^C16_NCU_CANARY_NATIVE_PASS ' "$run_dir/native_output.txt" || {
  echo "FAIL_NATIVE_VALIDATION" >&2
  exit 2
}

{
  printf 'research_user=%s\nuid=%s\ngid=%s\ngroups=%s\n' "$(id -un)" "$(id -u)" "$(id -g)" "$(id -nG)"
  printf 'CUDA_VISIBLE_DEVICES=%s\n' "${CUDA_VISIBLE_DEVICES:-UNSET}"
  printf 'gpu=%s\nkernel=%s\ncuda_symlink=%s\n' "$gpu_line" "$(uname -r)" "$(readlink -f /usr/local/cuda)"
  printf 'ncu_path=%s\n' "$(realpath "$ncu")"
  "$ncu" --version
  printf 'metric=%s\n' "$metric"
  printf 'report=%s\nwall_timeout_seconds=120\n' "$report"
  printf 'pre_profile_compute_processes:\n'
  nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader || true
} >"$run_dir/pre_profile_identity.txt"

ncu_argv=("$ncu" --target-processes application-only --replay-mode kernel \
  --kernel-name-base function --kernel-name c16_vector_add_kernel --metrics "$metric" \
  --export "$report_base" "$binary")
printf '%q ' "${ncu_argv[@]}" >"$run_dir/ncu_argv.txt"; printf '\n' >>"$run_dir/ncu_argv.txt"

set +e
timeout --foreground 120s "${ncu_argv[@]}" >"$run_dir/ncu_stdout_stderr.txt" 2>&1
ncu_rc=$?
set -e
if [[ $ncu_rc -ne 0 ]]; then
  if grep -q 'ERR_NVGPUCTRPERM' "$run_dir/ncu_stdout_stderr.txt"; then
    printf 'NCU_N1_ERR_NVGPUCTRPERM_FAIL_CLOSED\n' >"$run_dir/status.txt"
  else
    printf 'NCU_N1_PROFILE_FAILURE_EXIT_%s\n' "$ncu_rc" >"$run_dir/status.txt"
  fi
  sha256sum "$source_file" "$binary" "$metric_file" "$run_dir"/* >"$run_dir/SHA256SUMS.txt"
  exit "$ncu_rc"
fi

[[ -s $report ]] || { echo 'NCU_N1_MISSING_REPORT' >"$run_dir/status.txt"; exit 1; }
"$ncu" --import "$report" --page raw --csv >"$run_dir/report_raw.csv" 2>"$run_dir/report_import_stderr.txt"
grep -Fq "$metric" "$run_dir/report_raw.csv" || {
  echo 'NCU_N1_EXPORT_MISSING_METRIC' >"$run_dir/status.txt"
  exit 1
}

{
  printf 'post_profile_compute_processes:\n'
  nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader || true
  printf 'ncu_process_check:\n'
  pgrep -af '/opt/nvidia/nsight-compute/2025.1.1/ncu' || true
} >"$run_dir/post_profile_process_check.txt"

printf 'NCU_N1_HARDWARE_COUNTER_CANARY_PASS\n' >"$run_dir/status.txt"
sha256sum "$source_file" "$binary" "$metric_file" "$report" "$run_dir"/* >"$run_dir/SHA256SUMS.txt"
printf 'N1 PASS run_dir=%s report=%s\n' "$run_dir" "$report"
