#!/usr/bin/env bash
# Fetch only the hash-closed 66-wheel C16 CP310 runtime closure, then verify it.
set -euo pipefail
umask 077

usage() { echo "usage: $0 --materialize" >&2; }
[[ $# -eq 1 && $1 == --materialize ]] || { usage; exit 2; }
[[ $EUID -ne 0 && $(id -un) == huangrulin ]] || { echo "must run as huangrulin, not root" >&2; exit 2; }

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
manifest="$repo/docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g/WHEELHOUSE_MANIFEST.tsv"
requirements="$repo/util/vm_tlb/c16/lane_g/requirements.lock"
python=/data/c16/env/c16-py310/bin/python
python_lib=/data/c16/env/cpython-3.10.12/lib
deps_lib=/data/c16/env/build-deps-cpython310/lib
wheelhouse=/data/c16/wheelhouse/c16-g-cp310-cu124
stamp=$(date -u +%Y%m%dT%H%M%SZ)
receipt=/data/c16/results/C16_U2_WHEELHOUSE_MATERIALIZE_$stamp
expected_manifest_sha=ebae0934de68b36e08da5db0e6bfdc47880620205e8bf6d8c8afe8906abc2d2d
expected_requirements_sha=8085caecebf1e641cb6ab1f2c0e2d8e8cfd5007fd8236b6c10771b223052fa82

[[ -x $python && -f $manifest && -f $requirements ]] || { echo "missing Python/authority inputs" >&2; exit 2; }
[[ $(sha256sum "$manifest" | awk '{print $1}') == "$expected_manifest_sha" ]] || { echo "manifest hash mismatch" >&2; exit 1; }
[[ $(sha256sum "$requirements" | awk '{print $1}') == "$expected_requirements_sha" ]] || { echo "requirements hash mismatch" >&2; exit 1; }
mkdir -p "$wheelhouse" "$receipt"
cp "$manifest" "$wheelhouse/WHEELHOUSE_MANIFEST.tsv"
cp "$requirements" "$wheelhouse/requirements.lock"

export LD_LIBRARY_PATH="$python_lib:$deps_lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
while IFS=$'\t' read -r filename package version size expected_sha source compatibility status; do
  [[ $filename == wheel_filename ]] && continue
  target="$wheelhouse/$filename"
  if [[ -e $target ]]; then
    actual_sha=$(sha256sum "$target" | awk '{print $1}')
    actual_size=$(stat -c %s "$target")
    [[ $actual_sha == "$expected_sha" && $actual_size == "$size" ]] || {
      echo "existing wheel mismatch: $filename" >&2
      exit 1
    }
    printf 'REUSED\t%s\n' "$filename" >>"$receipt/downloads.tsv"
    continue
  fi
  if [[ $package == torch ]]; then
    cmd=("$python" -m pip download --disable-pip-version-check --only-binary=:all: --no-deps --dest "$wheelhouse" --index-url https://download.pytorch.org/whl/cu124 "$package==$version")
  else
    cmd=("$python" -m pip download --disable-pip-version-check --only-binary=:all: --no-deps --dest "$wheelhouse" "$package==$version")
  fi
  printf '%q ' "${cmd[@]}" >>"$receipt/COMMANDS.txt"; printf '\n' >>"$receipt/COMMANDS.txt"
  "${cmd[@]}" >>"$receipt/pip_download.log" 2>&1
  [[ -e $target ]] || { echo "expected filename not produced: $filename" >&2; exit 1; }
  actual_sha=$(sha256sum "$target" | awk '{print $1}')
  actual_size=$(stat -c %s "$target")
  [[ $actual_sha == "$expected_sha" && $actual_size == "$size" ]] || {
    echo "downloaded wheel hash/size mismatch: $filename" >&2
    exit 1
  }
  printf 'DOWNLOADED\t%s\n' "$filename" >>"$receipt/downloads.tsv"
done <"$manifest"

awk 'NR > 1 {print $5 "  " $1}' "$manifest" | (cd "$wheelhouse" && sha256sum -c -) >"$receipt/manifest_sha256_check.txt" 2>&1
[[ $(find "$wheelhouse" -maxdepth 1 -type f -name '*.whl' | wc -l) -eq 66 ]] || { echo "wheel count is not 66" >&2; exit 1; }
sha256sum "$wheelhouse/WHEELHOUSE_MANIFEST.tsv" "$wheelhouse/requirements.lock" >"$receipt/authority_sha256.txt"
sha256sum "$receipt"/* >"$receipt/SHA256SUMS.txt"
printf 'WHEELHOUSE_MATERIALIZE_PASS wheelhouse=%s receipt=%s\n' "$wheelhouse" "$receipt"
