#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: run_common_capture.sh --framework-root DIR --base-work-root DIR --work-root DIR [--runner FILE] [--case IDS] [--phase native|discovery|trace]

Uses the proven TLS/C2P campaign runner with the separately versioned common
manifest.  Run native and discovery before trace.  Trace is serial and
resumable; use offload_archives.sh from the TLS/C2P campaign on the SSH host
to move each verified archive off AutoDL before the next large case.
EOF
}

framework_root=""
base_work_root=""
work_root=""
case="all"
phase=""
runner="${CAMPAIGN_RUNNER:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root="$2"; shift 2 ;;
    --base-work-root) base_work_root="$2"; shift 2 ;;
    --work-root) work_root="$2"; shift 2 ;;
    --runner) runner="$2"; shift 2 ;;
    --case) case="$2"; shift 2 ;;
    --phase) phase="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$framework_root" && -n "$base_work_root" && -n "$work_root" && -n "$phase" ]] || { usage >&2; exit 2; }
[[ "$phase" =~ ^(native|discovery|trace)$ ]] || { echo "error: unsupported --phase" >&2; exit 2; }
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "$runner" ]]; then
  runner="$script_dir/../../v100_trace_campaign/scripts/campaign.py"
fi
manifest="$script_dir/../manifest.json"
[[ -f "$runner" && -f "$manifest" ]] || { echo "error: missing campaign runner or manifest" >&2; exit 1; }

if [[ "$phase" == "trace" ]]; then
  min_free=100
else
  min_free=1
fi
python3 "$runner" run --framework-root "$framework_root" --work-root "$work_root" \
  --manifest "$manifest" --phase "$phase" --case "$case" --minimum-free-gib "$min_free"
