#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: stage_inputs.sh --work-root DIR

Stages only the C2P candidate files into WORK_ROOT/inputs and writes a SHA256
lock file.  It prefers files from WORK_ROOT/input-seed, then falls back to an
already extracted gpu-app-collection data_dirs tree.  This keeps a required
four-file campaign from downloading the complete multi-gigabyte suite archive.
EOF
}

work_root=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-root) work_root="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$work_root" ]] || { echo "error: --work-root is required" >&2; exit 2; }
work_root="$(cd "$work_root" && pwd)"
gpuapps="$work_root/src/gpu-app-collection"
[[ -x "$gpuapps/get_data.sh" ]] || { echo "error: build_workloads.sh must complete first" >&2; exit 1; }

input_root="$work_root/inputs"
seed_root="${INPUT_SEED_ROOT:-$work_root/input-seed}"
mkdir -p "$input_root/ispass" "$input_root/pannotia"
declare -A files=(
  ["$gpuapps/data_dirs/cuda/ispass-2009/ispass-2009-BFS/data/graph65536.txt"]="$input_root/ispass/graph65536.txt"
  ["$gpuapps/data_dirs/pannotia/ecology1.graph"]="$input_root/pannotia/ecology1.graph"
  ["$gpuapps/data_dirs/pannotia/256_16384.gr"]="$input_root/pannotia/256_16384.gr"
  ["$gpuapps/data_dirs/pannotia/coAuthorsDBLP.graph"]="$input_root/pannotia/coAuthorsDBLP.graph"
)
for source in "${!files[@]}"; do
  target="${files[$source]}"
  seed="$seed_root/$(basename "$target")"
  if [[ -f "$seed" ]]; then
    cp -a "$seed" "$target"
  elif [[ -f "$source" ]]; then
    cp -a "$source" "$target"
  else
    echo "error: missing input $(basename "$target"): provide $seed or extracted upstream $source" >&2
    exit 1
  fi
done

lock="$input_root/inputs.lock.generated.json"
python3 - "$lock" "$input_root" <<'PY'
import hashlib
import json
import pathlib
import sys

lock, root = map(pathlib.Path, sys.argv[1:])
files = []
for path in sorted(p for p in root.rglob('*') if p.is_file() and p.name != lock.name):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    files.append({"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": digest})
lock.write_text(json.dumps({"schema": "accel-sim-v100-input-lock-v1", "files": files}, indent=2) + "\n")
PY
printf 'PASS staged_inputs=%s lock=%s\n' "$(find "$input_root" -type f | wc -l | tr -d ' ')" "$lock"
