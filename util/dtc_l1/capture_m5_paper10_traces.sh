#!/usr/bin/env bash
# Capture exact M5 Paper-10 traces.  This is deliberately fail-closed: an
# identity, application-check, trace, postprocess, or tracer-error failure
# aborts the workload and the entire invocation.
set -euo pipefail

usage() { cat <<'EOF'
usage: capture_m5_paper10_traces.sh --polybench-src DIR --spmv-wrapper DIR \
  --parboil-src DIR --spmv-input-dir DIR --spmv-reference FILE \
  --tracer-so FILE --postprocess FILE --out DIR
Requires a single NVIDIA V100 exposed by CUDA_VISIBLE_DEVICES, CUDA 11.8 NVCC,
and NVBit 1.8 tracer built from the checked-out Framework source.  Output is
external evidence; do not place it in a Git worktree.
EOF
}

polybench= wrapper= parboil= input_dir= reference= tracer= postprocess= out=
while [[ $# -gt 0 ]]; do
  case $1 in
    --polybench-src) polybench=$2; shift 2;; --spmv-wrapper) wrapper=$2; shift 2;;
    --parboil-src) parboil=$2; shift 2;; --spmv-input-dir) input_dir=$2; shift 2;;
    --spmv-reference) reference=$2; shift 2;; --tracer-so) tracer=$2; shift 2;;
    --postprocess) postprocess=$2; shift 2;; --out) out=$2; shift 2;;
    -h|--help) usage; exit 0;; *) usage >&2; exit 2;;
  esac
done
[[ -n $polybench && -n $wrapper && -n $parboil && -n $input_dir && -n $reference && -n $tracer && -n $postprocess && -n $out ]] || { usage >&2; exit 2; }
[[ ${CUDA_VISIBLE_DEVICES:-} != "" ]] || { echo 'FAIL CUDA_VISIBLE_DEVICES must select one V100' >&2; exit 2; }
[[ -x $tracer && -x $postprocess && -f $reference ]] || { echo 'FAIL missing tracer, postprocess, or SpMV reference' >&2; exit 2; }
nvcc=${NVCC:-/usr/local/cuda-11.8/bin/nvcc}
[[ -x $nvcc ]] || { echo "FAIL nvcc unavailable: $nvcc" >&2; exit 2; }
"$nvcc" --version | grep -q 'release 11.8' || { echo 'FAIL exact CUDA 11.8 toolchain required' >&2; exit 2; }
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | grep -qi 'V100' || { echo 'FAIL a V100 is required for this capture contract' >&2; exit 2; }

root=$(cd "$(dirname "$0")/../.." && pwd)
manifest="$root/docs/dtc_l1/m5/trace/PAPER10_TRACE_CAPTURE_MANIFEST.tsv"
[[ -f $manifest ]] || { echo "FAIL missing manifest: $manifest" >&2; exit 2; }
mkdir -p "$out"
[[ ! -e "$out/SHA256SUMS" ]] || { echo "FAIL refusing to mix with existing capture: $out" >&2; exit 2; }
build="$out/.build"; mkdir -p "$build"

declare -A src_sha=(
  [bicg]=e6a480c75f939958edd2633d7dc1be0a14d9890c6adb7b916b0db5e2c75965bd
  [atax]=5966799837bce3d7fce603c7876f78c2c1bc487f97f590bf242e28ab2acbd230
  [gemv]=c53e178dd285504f9dd29479460f85f25fa8fcd2e40a8429bf9f5e16e14de704
  [mvt]=44aa960a339f3702e82f4e9b2e7b29c90fae19b5a095fa1ccd0f8e6f6b76a87d
  [syrk]=7e208416e8b6c59b52ab9c2ba295c06802c2d1b48968374be6a6d6a618948f1f
  [gesu]=717c2bc6161a1d9b478282dabe994e0184821ee100996a898aba688302f384a4
  [syr2k]=6e25029d1b77d257ed41ddee95f54ce22c4dd6ed026b53a6ee1e1d82c362f960
  [2mm]=dec4988b28f94c75dfdc3b3048e1dc01511fb8cfcdc0314552451002be9d4a0f
  [2dconv]=cef6d23d7c1d931e5427175dcf4c02a2d5e81ca2747b133222ad962d63b390d8 )
declare -A source_rel=([bicg]=CUDA/BICG/bicg.cu [atax]=CUDA/ATAX/atax.cu [gemv]=CUDA/GEMVER/gemver.cu [mvt]=CUDA/MVT/mvt.cu [syrk]=CUDA/SYRK/syrk.cu [gesu]=CUDA/GESUMMV/gesummv.cu [syr2k]=CUDA/SYR2K/syr2k.cu [2mm]=CUDA/2MM/2mm.cu [2dconv]=CUDA/2DCONV/2DConvolution.cu)
declare -A exe=([bicg]=bicg [atax]=atax [gemv]=gemver [mvt]=mvt [syrk]=syrk [gesu]=gesummv [syr2k]=syr2k [2mm]=twomm [2dconv]=twodconv [spmv]=spmv)
declare -A exe_sha=([bicg]=db1cc9246ee97389b32396d3b20294a3c8a89139067cabcda93ec87d0ed1f84b [atax]=647851e4573103f853373323fe7cf779e363c2fb0242fe22089f64fd7d2db163 [gemv]=04d6c9b931988faf7f715eeda40f7688e0fee98b4b114a0c86d4a0f6da2dce5d [mvt]=7baa7b6b06b4e7868d836a01e11f0e435a76f10d989f1107bcbaea71bd0b9d8b [syrk]=e711f0dd94a2db64b746a24d34bff1fca9a634814e2978cf4efa058718f0af30 [gesu]=32da3ab10c6b0cdb0a7e9af569899e51ebb302a19602f9d37e3377469ab6447e [syr2k]=1cbb363142092a6a72dfc787db63cfeb864fa0dfe2b403ff7fcf6b098b734978 [2mm]=549c0a64248596af597c1b33894608bfa32fd5e59edcd4937ac6ccc4f2d3bcf1 [2dconv]=8ade2d6153cdaa9816cb6c4bc4d65320fe12c0b4fa9f18f90db7d50fd4831bc1 [spmv]=08f834ff68e9e092db1f988974ddb8491bba06c176037e862aa81b839ec5900c)

check_sha() { [[ $(sha256sum "$1" | awk '{print $1}') == "$2" ]] || { echo "FAIL SHA identity: $1" >&2; exit 1; }; }
tree_digest() { (cd "$1" && git ls-files -z | sort -z | xargs -0 sha256sum) | sha256sum | awk '{print $1}'; }
[[ $(git -C "$polybench" rev-parse HEAD) == 5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c ]] || { echo 'FAIL PolyBench commit identity' >&2; exit 1; }
[[ $(git -C "$wrapper" rev-parse HEAD) == de9cf4293f418877aa9cdb6a2395338ca06674a6 ]] || { echo 'FAIL SpMV wrapper commit identity' >&2; exit 1; }
[[ $(git -C "$parboil" rev-parse HEAD) == 4e0fc54866546efa44fe93af57c9cef62f6c8eb9 ]] || { echo 'FAIL Parboil commit identity' >&2; exit 1; }
for w in bicg atax gemv mvt syrk gesu syr2k 2mm 2dconv; do check_sha "$polybench/${source_rel[$w]}" "${src_sha[$w]}"; done
check_sha "$input_dir/bcsstk18.mtx" abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9
check_sha "$input_dir/vector.bin" d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061
"$root/util/dtc_l1/build_m5_polybench_cuda.sh" "$polybench" "$build/polybench"
"$root/util/dtc_l1/build_m5_parboil_spmv.sh" "$wrapper" "$parboil" "$build/spmv"
for w in bicg atax gemv mvt syrk gesu syr2k 2mm 2dconv; do check_sha "$build/polybench/${exe[$w]}" "${exe_sha[$w]}"; done
check_sha "$build/spmv/spmv" "${exe_sha[spmv]}"
cp "$manifest" "$out/manifest.tsv"
{ date -u +capture_utc=%FT%TZ; nvidia-smi; "$nvcc" --version; sha256sum "$tracer" "$postprocess"; git -C "$root" rev-parse HEAD; } > "$out/environment.txt"
{
  echo -e 'item\tsha256_or_commit'
  echo -e "polybench_commit\t$(git -C "$polybench" rev-parse HEAD)"
  echo -e "polybench_source_tree\t$(tree_digest "$polybench")"
  echo -e "spmv_wrapper_commit\t$(git -C "$wrapper" rev-parse HEAD)"
  echo -e "spmv_wrapper_source_tree\t$(tree_digest "$wrapper")"
  echo -e "parboil_commit\t$(git -C "$parboil" rev-parse HEAD)"
  echo -e "parboil_source_tree\t$(tree_digest "$parboil")"
  sha256sum "$input_dir/bcsstk18.mtx" "$input_dir/vector.bin" "$reference" "$build"/polybench/* "$build/spmv/spmv"
} > "$out/identity.tsv"

capture_one() {
  local w=$1 bin=$2; shift 2; local d="$out/$w"; mkdir -p "$d"; (
    cd "$d"
    env -u DYNAMIC_KERNEL_RANGE CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" LD_PRELOAD="$tracer" "$bin" "$@" >capture.log 2>&1
    if [[ $w == spmv ]]; then "$root/util/dtc_l1/verify_m5_parboil_spmv_output.py" "$reference" result.bin >correctness.log 2>&1; else "$root/util/dtc_l1/verify_m5_polybench_output.py" "$w" capture.log >correctness.log 2>&1; fi
    [[ -s traces/kernelslist && -s traces/stats.csv ]] || { echo "FAIL missing raw trace list/stats" >&2; exit 1; }
    "$postprocess" traces/kernelslist >>capture.log 2>&1
    [[ -s traces/kernelslist.g ]] && compgen -G 'traces/kernel-*.trace' >/dev/null && compgen -G 'traces/kernel-*.traceg' >/dev/null || { echo "FAIL incomplete grouped trace" >&2; exit 1; }
    ! grep -Eqi '(fatal|assert|error)' capture.log || { echo "FAIL tracer/application error scan" >&2; exit 1; }
    mv traces/* .; rmdir traces
    awk 'NF' kernelslist | wc -l > kernel_count.txt; awk 'NF' kernelslist.g | wc -l > grouped_kernel_count.txt
    [[ $(cat kernel_count.txt) -eq $(cat grouped_kernel_count.txt) ]] || { echo "FAIL raw/grouped kernel count mismatch" >&2; exit 1; }
  )
}
for w in bicg atax gemv mvt syrk gesu syr2k 2mm 2dconv; do capture_one "$w" "$build/polybench/${exe[$w]}"; done
capture_one spmv "$build/spmv/spmv" -i "$input_dir/bcsstk18.mtx,$input_dir/vector.bin" -o result.bin
(cd "$out" && find . -type f ! -path './.build/*' -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
echo "PASS exact Paper-10 capture complete: $out"
