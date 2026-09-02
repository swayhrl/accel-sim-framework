#!/usr/bin/env bash
# No-GPU proof of the Route-E child environment contract.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
recorder="$tmp/record.sh"
printf '%s\n' '#!/usr/bin/env bash' 'printf "%s|%s\\n" "$RANK" "${CUDA_INJECTION64_PATH-ABSENT}"' > "$recorder"
chmod +x "$recorder"

for phase in smoke trace; do
  : > "$tmp/$phase.out"
  for rank in 0 1 2 3; do
    CUDA_INJECTION64_PATH=parent-leak M4A_PHASE="$phase" RANK="$rank" M4A_NVBIT_PATH=/frozen/tracer.so \
      "$script_dir/rank0_nvbit_exec.sh" "$recorder" >> "$tmp/$phase.out"
  done
done
expected_smoke=$'0|ABSENT\n1|ABSENT\n2|ABSENT\n3|ABSENT'
expected_trace=$'0|/frozen/tracer.so\n1|ABSENT\n2|ABSENT\n3|ABSENT'
[[ "$(cat "$tmp/smoke.out")" == "$expected_smoke" ]] || { cat "$tmp/smoke.out" >&2; exit 1; }
[[ "$(cat "$tmp/trace.out")" == "$expected_trace" ]] || { cat "$tmp/trace.out" >&2; exit 1; }
if M4A_PHASE=trace M4A_NVBIT_PATH=/frozen/tracer.so "$script_dir/rank0_nvbit_exec.sh" true 2>/dev/null; then
  echo "missing RANK unexpectedly passed" >&2; exit 1
fi
if M4A_PHASE=trace RANK=4 M4A_NVBIT_PATH=/frozen/tracer.so "$script_dir/rank0_nvbit_exec.sh" true 2>/dev/null; then
  echo "inconsistent RANK unexpectedly passed" >&2; exit 1
fi
echo "PASS rank0-only NVBit mock: smoke none; trace rank0 only"
