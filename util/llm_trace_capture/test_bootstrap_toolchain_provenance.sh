#!/usr/bin/env bash
# No-GPU fake-toolchain proof that selected CUDA A defeats PATH CUDA B.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
framework="$tmp/framework"; work="$tmp/work"; selected="$tmp/cuda-A"; contaminant="$tmp/cuda-B"; fakebin="$tmp/fakebin"
mkdir -p "$framework/util/tracer_nvbit/tracer_tool/traces-processing" "$work" "$selected/bin" "$contaminant/bin" "$fakebin"
for toolkit in "$selected" "$contaminant"; do
  label="$(basename "$toolkit")"
  printf '#!/usr/bin/env bash\nprintf "release %s\\n" "'$label'"\n' > "$toolkit/bin/nvcc"
  printf '#!/usr/bin/env bash\nprintf "ptxas %s\\n" "'$label'"\n' > "$toolkit/bin/ptxas"
  chmod +x "$toolkit/bin/nvcc" "$toolkit/bin/ptxas"
done
cat > "$fakebin/make" <<'EOF'
#!/usr/bin/env bash
printf 'NVCC=%s\nPTXAS=%s\nPATH_NVCC=%s\nPATH_PTXAS=%s\n' "$NVCC" "$PTXAS" "$(command -v nvcc)" "$(command -v ptxas)" >> "$MAKE_AUDIT"
exit 0
EOF
chmod +x "$fakebin/make"
MAKE_AUDIT="$work/audit" PATH="$fakebin:$contaminant/bin:$PATH" \
  "$script_dir/build_nvbit_with_toolchain.sh" --framework-root "$framework" --work-root "$work" --cuda-home "$selected" >/dev/null
audit="$(cat "$work/audit")"
[[ "$audit" == *"NVCC=$selected/bin/nvcc"* && "$audit" == *"PTXAS=$selected/bin/ptxas"* ]] || { echo "$audit" >&2; exit 1; }
[[ "$audit" == *"PATH_NVCC=$selected/bin/nvcc"* && "$audit" == *"PATH_PTXAS=$selected/bin/ptxas"* ]] || { echo "$audit" >&2; exit 1; }
[[ "$audit" != *"$contaminant/bin"* ]] || { echo "$audit" >&2; exit 1; }
echo "PASS fake-toolchain bootstrap: selected A used; PATH B excluded"
