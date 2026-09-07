#!/usr/bin/env bash
# Prepare the researcher-authorized FAST64.2 source-reachable lower-cap /
# candidate-queue coupling stress.  --launch is deliberately audit-gated and
# never addresses any historical namespace.
set -euo pipefail

usage() {
  echo "usage: $0 [--dry-run | --materialize | --launch --resource-audit FILE]" >&2
  exit 2
}

action=dry-run audit=
if [ "$#" -gt 0 ]; then
  case "$1" in
    --dry-run) shift ;;
    --materialize) action=materialize; shift ;;
    --launch) action=launch; shift ;;
    *) usage ;;
  esac
fi
if [ "$action" = launch ]; then
  test "${1:-}" = --resource-audit || usage
  audit=${2:-}
  shift 2
fi
test "$#" = 0 || usage

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
runs_root=/workspace/fast64-runs
core_root=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
expected_core=bbcbb5e7565417102087bc80b14c349b4e568c05
scientific_config_source=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out
expected_runtime=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer_sha=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e
runner_source="$repo_root/util/dtc_l1/run_fast64_trace_v2.sh"
materializer="$repo_root/util/dtc_l1/materialize_fast64_coupled_lower_cap_stress_config.sh"
trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
source_config="$repo_root/configs/dtc_l1/fast64/FAST64_IO.config"
config="$runs_root/overlays/FAST64_IO_COUPLED_STRESS_CAP512_PIB1.config"
provenance="$config.PROVENANCE.tsv"
row=fast64_2_precomputed_nn_io_coupled_cap512_pib1_a1_r2
run_dir="$runs_root/$row"
cpu=81
classification=PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE
immutable_root=/tmp/fast64-runners

test "$(git -C "$core_root" rev-parse HEAD)" = "$expected_core"
test -x "$runtime" && test "$(sha256sum "$runtime" | awk '{print $1}')" = "$expected_runtime"
test -x "$runner_source" && test -x "$materializer" && test -r "$trace_config" && test -r "$source_config"
trace_root=$(awk -F '\t' '$1 == "nn" { print $2; exit }' "$repo_root/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv")
test -n "$trace_root" && test -r "$trace_root/kernelslist.g"
runner_sha=$(sha256sum "$runner_source" | awk '{print $1}')
immutable_dir="$immutable_root/$runner_sha"
immutable_runner="$immutable_dir/run_fast64_trace_v2.sh"

if [ "$action" = materialize ]; then
  "$materializer" --mode IO --source-config "$source_config" --output-config "$config" \
    --entries 1 --lower-cap 512
  echo "FAST64_2_COUPLED_STRESS_CONFIG_MATERIALIZED config=$config"
  exit 0
fi

if [ "$action" = dry-run ]; then
  test ! -e "$run_dir" || { echo "COUPLED_STRESS_NAMESPACE_ALREADY_EXISTS $run_dir" >&2; exit 1; }
  printf 'FAST64_2_COUPLED_STRESS_DRY_RUN_PASS\trow=%s\tworkload=NN\tmode=IO\tentries=1\tlower_cap=512\tconfig=%s\tconfig_materialized=%s\trunner_sha256=%s\n' \
    "$row" "$config" "$([ -f "$config" ] && echo YES || echo NO)" "$runner_sha"
  exit 0
fi

test -r "$audit" || { echo "COUPLED_STRESS_RESOURCE_AUDIT_UNAVAILABLE" >&2; exit 1; }
authorized=$(awk -F '\t' '
  $1 == "schema" && $2 == "FAST64_R2_RESOURCE_AUDIT_V1" { schema=1 }
  $1 == "safe_to_launch" && $2 == "YES" { safe=1 }
  $1 == "fast64_2_coupled_stress_authorized" && $2 == "YES" { stress=1 }
  $1 == "authorized_workers" && $2 ~ /^[1-7]$/ { workers=1 }
  $1 == "memavailable_bytes" && $2 ~ /^[0-9]+$/ { mem=1 }
  $1 == "memory_current_bytes" && $2 ~ /^[0-9]+$/ { current=1 }
  $1 == "memory_max_bytes" && $2 ~ /^[0-9]+$/ { maximum=1 }
  $1 == "swap_si_delta" && $2 ~ /^[0-9]+$/ { si=1 }
  $1 == "swap_so_delta" && $2 ~ /^[0-9]+$/ { so=1 }
  $1 == "oom_kill_delta" && $2 ~ /^[0-9]+$/ { oom=1 }
  $1 == "p95_rss_bytes" && $2 ~ /^[0-9]+$/ { rss=1 }
  $1 == "iowait_pct" && $2 ~ /^[0-9.]+$/ { iowait=1 }
  $1 == "output_free_bytes" && $2 ~ /^[0-9]+$/ { output=1 }
  END { exit !(schema && safe && stress && workers && mem && current && maximum && si && so && oom && rss && iowait && output) }
' "$audit") || { echo "COUPLED_STRESS_RESOURCE_AUDIT_INCOMPLETE_OR_UNSAFE" >&2; exit 1; }
test -r "$config" && test -r "$provenance" || { echo "COUPLED_STRESS_CONFIG_NOT_MATERIALIZED" >&2; exit 1; }
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$config" | tail -1)" = '-gpgpu_dtc_l1_lower_outstanding_cap 512'
test "$(grep -Fxc -- '-gpgpu_dtc_l1_io_pib_entries 1' "$config")" = 1
test "$(awk -F '\t' '$1 == "output_config_sha256" {print $2}' "$provenance")" = "$(sha256sum "$config" | awk '{print $1}')"
test ! -e "$run_dir" && test ! -e "$run_dir.launcher.log" && test ! -e "$run_dir.supervisor.tsv" || {
  echo "COUPLED_STRESS_TARGET_EXISTS" >&2; exit 1;
}

mkdir -p "$immutable_dir"
if [ ! -e "$immutable_runner" ]; then
  cp -- "$runner_source" "$immutable_runner"
  chmod 555 "$immutable_runner"
fi
test "$(sha256sum "$immutable_runner" | awk '{print $1}')" = "$runner_sha"
test $((8#$(stat -c %a "$immutable_runner") & 0222)) -eq 0
chmod 555 "$immutable_dir"

exec 9>"$runs_root/.fast64_2_coupled_stress_dispatch.lock"
flock -n 9 || { echo "COUPLED_STRESS_DISPATCH_LOCK_HELD" >&2; exit 1; }
attempt_uuid=$(cat /proc/sys/kernel/random/uuid)
setsid "$immutable_runner" --simulator "$runtime" --config "$config" \
  --trace "$trace_root/kernelslist.g" --trace-config "$trace_config" --run-dir "$run_dir" --cpu "$cpu" \
  --attempt-uuid "$attempt_uuid" --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable_runner" \
  --framework-scientific-config-source-sha "$scientific_config_source" --core-source-head "$expected_core" \
  --observer-overlay-sha "$observer_sha" --result-classification "$classification" \
  >"$run_dir.launcher.log" 2>&1 9>&- &
supervisor=$!
printf 'row\tsupervisor_pid\tattempt_uuid\trunner_sha256\timmutable_runner\tcore_sha\truntime_sha256\tconfig_sha256\tclassification\n' >"$run_dir.supervisor.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$row" "$supervisor" "$attempt_uuid" "$runner_sha" \
  "$immutable_runner" "$expected_core" "$expected_runtime" "$(sha256sum "$config" | awk '{print $1}')" "$classification" >>"$run_dir.supervisor.tsv"
echo "FAST64_2_COUPLED_STRESS_DISPATCHED row=$row supervisor=$supervisor attempt_uuid=$attempt_uuid"
