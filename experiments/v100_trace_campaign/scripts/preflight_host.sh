#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: preflight_host.sh --framework-root DIR --work-root DIR [--minimum-free-gib N]

Validates an AutoDL host before any source download or tracing. It does not
install packages and makes no changes outside --work-root.
EOF
}

framework_root=""
work_root=""
minimum_free_gib=800
while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root) framework_root="$2"; shift 2 ;;
    --work-root) work_root="$2"; shift 2 ;;
    --minimum-free-gib) minimum_free_gib="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# AutoDL exposes CUDA from /etc/profile.d in interactive shells, but a tmux
# pane or non-interactive SSH command may not source that file.  Keep the
# campaign independent of shell startup policy.
cuda_home="${CUDA_HOME:-/usr/local/cuda}"
if [[ -x "$cuda_home/bin/nvcc" ]]; then
  export PATH="$cuda_home/bin:$PATH"
fi

[[ -d "$framework_root" ]] || { echo "error: --framework-root must exist" >&2; exit 2; }
[[ -n "$work_root" ]] || { echo "error: --work-root is required" >&2; exit 2; }
[[ "$minimum_free_gib" =~ ^[0-9]+$ ]] || { echo "error: --minimum-free-gib must be an integer" >&2; exit 2; }
mkdir -p "$work_root"
framework_root="$(cd "$framework_root" && pwd)"
work_root="$(cd "$work_root" && pwd)"

required=(bash python3 git curl unzip make g++ rsync zstd sha256sum tar nvidia-smi nvcc)
missing=()
for cmd in "${required[@]}"; do
  command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd")
done
if (( ${#missing[@]} )); then
  printf 'error: missing commands: %s\n' "${missing[*]}" >&2
  echo "Install them in the selected AutoDL image before continuing." >&2
  exit 1
fi

[[ -x "$framework_root/util/tracer_nvbit/tracer_tool/tracer_tool.so" ]] || {
  echo "error: missing built tracer: $framework_root/util/tracer_nvbit/tracer_tool/tracer_tool.so" >&2
  echo "Run: cd $framework_root/util/tracer_nvbit && ./install_nvbit.sh && ./make" >&2
  exit 1
}
[[ -x "$framework_root/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing" ]] || {
  echo "error: missing post-traces-processing binary" >&2; exit 1;
}

gpu_info="$(nvidia-smi --query-gpu=name,compute_cap,driver_version,memory.total --format=csv,noheader 2>&1)"
printf '%s\n' "$gpu_info"
gpu_count="$(printf '%s\n' "$gpu_info" | wc -l | tr -d ' ')"
[[ "$gpu_count" == "1" ]] || {
  echo "error: campaign is intentionally single-GPU; expected one visible GPU, saw $gpu_count" >&2; exit 1;
}
printf '%s\n' "$gpu_info" | grep -Eqi '(V100|Tesla V100).*7\.0' || {
  echo "error: expected one V100 with compute capability 7.0, got: $gpu_info" >&2; exit 1;
}
nvcc_version="$(nvcc --version)"
printf '%s\n' "$nvcc_version"
printf '%s\n' "$nvcc_version" | grep -q 'release 11\.8' || {
  echo "error: expected CUDA toolkit 11.8; select a CUDA 11.8 image or update PATH" >&2; exit 1;
}

free_kib="$(df -Pk "$work_root" | awk 'NR==2 {print $4}')"
free_gib=$(( free_kib / 1024 / 1024 ))
if (( free_gib < minimum_free_gib )); then
  echo "error: only ${free_gib} GiB free under $work_root; need at least ${minimum_free_gib} GiB" >&2
  exit 1
fi

report="$work_root/host-preflight.txt"
{
  printf 'timestamp_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'framework_root=%s\nwork_root=%s\n' "$framework_root" "$work_root"
  git -C "$framework_root" rev-parse HEAD 2>/dev/null || true
  nvidia-smi -q
  nvcc --version
  df -h "$work_root"
} > "$report"
printf 'PASS report=%s\n' "$report"
