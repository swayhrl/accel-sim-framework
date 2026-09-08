#!/usr/bin/env bash
# Future-only immutable-v2 dispatch for one non-redundant FAST64.3 Base row.
set -euo pipefail
usage(){ echo "usage: $0 --workload ID [--dry-run | --launch --resource-audit FILE]" >&2; exit 2; }
workload= mode=dry-run audit=
while [ "$#" -gt 0 ]; do case "$1" in --workload) workload=${2:-};shift 2;; --dry-run)shift;; --launch) mode=launch;test "${2:-}" = --resource-audit||usage;audit=${3:-};shift 3;; *)usage;;esac; done
test -n "$workload" || usage
case "$workload" in atax|gesummv|gemm|2DConvolution|btree|dwt2d|gaussian|hotspot1|lud|mri-q) ;; *) echo "BASE_V2_WORKLOAD_NOT_ELIGIBLE_FOR_NONREDUNDANT_PRECOMPUTE $workload" >&2; exit 2;; esac
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.."&&pwd); runs=/workspace/fast64-runs; core=/workspace/worktrees/gpgpu-sim-decoupled-l1-m5
core_sha=bbcbb5e7565417102087bc80b14c349b4e568c05; source_sha=037f008b330eb230353b60edf126d6be9f45afdc
runtime=/tmp/dtc-fast64-telemetry-build-sEWez4/accel-sim.out; runtime_sha=6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041
observer=2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e; runner_sha=bf9a84c8aab54ccd5d00a8465d69669cfac78012b783c3cfd9e0e4433062e6af
runner="$repo/util/dtc_l1/run_fast64_trace_v2.sh"; immutable="/tmp/fast64-runners/$runner_sha/run_fast64_trace_v2.sh"; config="$repo/configs/dtc_l1/fast64/FAST64_BASE.config"; trace_config="$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
row="fast64_3_precomputed_${workload}_base_cap8192_a1_r2"; dir="$runs/$row"; class=PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE
test "$(git -C "$core" rev-parse HEAD)" = "$core_sha"; git -C "$repo" rev-parse --verify "$source_sha^{commit}" >/dev/null
test -x "$runtime"&&test "$(sha256sum "$runtime"|awk '{print $1}')" = "$runtime_sha"; test -x "$runner"&&test "$(sha256sum "$runner"|awk '{print $1}')" = "$runner_sha"; test -x "$immutable"&&test "$(sha256sum "$immutable"|awk '{print $1}')" = "$runner_sha"&&test $((8#$(stat -c %a "$immutable")&0222)) -eq 0
test "$(sha256sum "$config"|awk '{print $1}')" = "$(git -C "$repo" show "$source_sha:configs/dtc_l1/fast64/FAST64_BASE.config"|sha256sum|awk '{print $1}')"; test "$(sha256sum "$trace_config"|awk '{print $1}')" = "$(git -C "$repo" show "$source_sha:gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"|sha256sum|awk '{print $1}')"
trace=$(awk -F '\t' -v w="$workload" '$1==w{print $2;exit}' "$repo/docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv"); test -n "$trace"&&test -r "$trace/kernelslist.g"
for p in "$dir" "$dir.launcher.log" "$dir.supervisor.tsv"; do test ! -e "$p"||{ echo "BASE_V2_TARGET_EXISTS $p" >&2;exit 1;};done
cpus=$(python3 "$repo/util/dtc_l1/select_fast64_r2_cpus.py" --format cpus); cpu=${cpus%%,*}; test -n "$cpu"
if [ "$mode" = dry-run ]; then printf 'FAST64_3_BASE_V2_DRY_RUN_PASS\trow=%s\tcpu=%s\n' "$row" "$cpu";exit 0;fi
test -r "$audit"; awk -F '\t' '$1=="schema"&&$2=="FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1"{s=1}$1=="safe_to_launch"&&$2=="YES"{y=1}$1=="authorized_workers"&&$2=="1"{w=1}$1=="swap_so_delta"&&$2=="0"{a=1}$1=="oom_kill_delta"&&$2=="0"{b=1}$1=="memory_psi_avg10"&&($2=="0"||$2=="0.00"){c=1}END{exit !(s&&y&&w&&a&&b&&c)}' "$audit"||{ echo BASE_V2_AUDIT_UNSAFE >&2;exit 1;}
exec 9>"$runs/.fast64_3_base_v2_dispatch.lock"; flock -n 9||{ echo BASE_V2_LOCK_HELD >&2;exit 1;}; uuid=$(cat /proc/sys/kernel/random/uuid)
( exec 9>&-; exec setsid "$immutable" --simulator "$runtime" --config "$config" --trace "$trace/kernelslist.g" --trace-config "$trace_config" --run-dir "$dir" --cpu "$cpu" --attempt-uuid "$uuid" --runner-sha256 "$runner_sha" --immutable-runner-path "$immutable" --framework-scientific-config-source-sha "$source_sha" --core-source-head "$core_sha" --observer-overlay-sha "$observer" --result-classification "$class" ) >"$dir.launcher.log" 2>&1 &
supervisor=$!; printf 'row\tsupervisor_pid\tcpu_slot\tattempt_uuid\trunner_sha256\tclassification\n%s\t%s\t%s\t%s\t%s\t%s\n' "$row" "$supervisor" "$cpu" "$uuid" "$runner_sha" "$class" >"$dir.supervisor.tsv"; printf 'FAST64_3_BASE_V2_DISPATCHED\trow=%s\tcpu=%s\tsupervisor=%s\n' "$row" "$cpu" "$supervisor"
