#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/fetch_decoupled_l2_large_archives.sh [--dest DIR]
       [--min-free-gib N]

Sequentially fetch the official legacy V100 Parboil, PolyBench, and CUTLASS
archives without extracting them.  Each transfer is guarded by
fetch_decoupled_l2_pretraces.sh, which verifies that the requested free-space
reserve survives the full archive download.
EOF
}

dest=""
min_free_gib=80
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest) dest="$2"; shift 2 ;;
    --min-free-gib) min_free_gib="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$min_free_gib" =~ ^[0-9]+$ ]] || {
  echo "error: --min-free-gib must be a nonnegative integer" >&2; exit 2;
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
args=(--archive-only --min-free-gib "$min_free_gib")
if [[ -n "$dest" ]]; then
  args+=(--dest "$dest")
fi
for suite in parboil polybench cutlass; do
  "$repo_root/scripts/fetch_decoupled_l2_pretraces.sh" --suite "$suite" "${args[@]}"
done
