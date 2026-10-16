#!/usr/bin/env bash
# CPU only. Includes CUDA headers for dim3; links no CUDA runtime or driver.
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
OUT=/data/c16/dtc_sm89_admission_feasibility_109_v1
cd "$REPO"
mkdir -p "$OUT/build" "$OUT/raw" "$OUT/assets/cubin"
python3 util/dtc_l1/sm89_admission_feasibility_v1/prepare_cpu.py
for variant in original fail_closed; do
  g++ -std=c++17 -O0 -g "$OUT/build/dispatch_$variant.cc" -o "$OUT/build/dispatch_$variant"
done
g++ -std=c++17 -O0 -g -I"$OUT/build" -I/usr/local/cuda-12.8/include -Igpu-simulator/trace-parser -Iutil/tracer_nvbit/tracer_tool gpu-simulator/trace-parser/trace_parser.cc util/dtc_l1/sm89_admission_feasibility_v1/parser_probe.cc -lzstd -pthread -o "$OUT/build/parser_probe" > "$OUT/raw/PARSER_BUILD.log" 2>&1
ldd "$OUT/build/parser_probe" > "$OUT/raw/PARSER_LINKED_LIBRARIES.txt"
if grep -Ei 'libcuda|libcudart' "$OUT/raw/PARSER_LINKED_LIBRARIES.txt"; then echo 'Unexpected GPU runtime dependency' >&2; exit 2; fi
git apply --check docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/candidate_fail_closed.patch
python3 util/dtc_l1/sm89_admission_feasibility_v1/audit_cpu.py > "$OUT/raw/CPU_AUDIT.log" 2>&1
# Offline inspection of the already measured immutable executable, never launch it.
(
 cd "$OUT/assets/cubin"
 /usr/local/cuda-12.8/bin/cuobjdump --extract-elf all /data/c16/dtc_native_coverage_109_v1/bin/spmv > "$OUT/raw/CUBIN_EXTRACTION.log"
 for f in *.cubin; do /usr/local/cuda-12.8/bin/nvdisasm -plr "$f" > "$f.liveness.txt"; done
)
printf 'CPU-only parser, coverage, rejection and offline liveness checks completed\n'
