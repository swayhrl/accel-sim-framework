#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_decoupled_l2_bank_diagnosis.sh --case NAME KERNELSLIST [--case NAME KERNELSLIST ...]
       --run-root DIR [--config FILE] [--trace-config FILE] [--build]

Runs matched baseline/decoupled pairs sequentially, then checks executable,
trace, and non-backend configuration identity while producing CSV/Markdown
bank-observability summaries.  Use a new run root for every rebuilt binary.
EOF
}

cases=()
run_root=""
config=""
trace_config=""
build=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --case) cases+=("$2" "$3"); shift 3 ;;
    --run-root) run_root="$2"; shift 2 ;;
    --config) config="$2"; shift 2 ;;
    --trace-config) trace_config="$2"; shift 2 ;;
    --build) build=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

(( ${#cases[@]} > 0 && ${#cases[@]} % 2 == 0 )) || {
  echo 'error: supply one or more --case NAME KERNELSLIST pairs' >&2; exit 2;
}
[[ -n "$run_root" ]] || { echo 'error: --run-root is required' >&2; exit 2; }
[[ -n "${DECOUPLED_L2_GPGPUSIM_ROOT:-}" ]] || {
  echo 'error: set DECOUPLED_L2_GPGPUSIM_ROOT' >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -z "$config" ]]; then
  config="$DECOUPLED_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config"
fi
if [[ -z "$trace_config" ]]; then
  trace_config="$repo_root/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
fi
[[ -f "$config" && -f "$trace_config" ]] || {
  echo 'error: config or trace-config is missing' >&2; exit 2;
}
mkdir -p "$run_root"
run_root="$(cd "$run_root" && pwd)"

first=1
analyze_args=()
for ((index=0; index<${#cases[@]}; index+=2)); do
  name="${cases[index]}"
  trace="${cases[index + 1]}"
  [[ -f "$trace" ]] || { echo "error: missing trace for $name: $trace" >&2; exit 2; }
  for backend in baseline decoupled; do
    args=(--backend "$backend" --trace "$trace" --config "$config"
          --trace-config "$trace_config" --run-dir "$run_root/$name/$backend")
    if [[ "$first" -eq 1 && "$build" -eq 1 ]]; then args+=(--build); fi
    "$repo_root/scripts/run_decoupled_l2_smoke.sh" "${args[@]}"
    first=0
  done
  analyze_args+=(--pair "$name" "$run_root/$name/baseline" "$run_root/$name/decoupled")
done

python3 "$repo_root/scripts/analyze_decoupled_l2_bank_observability.py" \
  "${analyze_args[@]}" --csv "$run_root/bank_observability.csv" \
  --markdown "$run_root/bank_observability.md"
printf 'PASS run_root=%s summary=%s\n' "$run_root" "$run_root/bank_observability.md"
