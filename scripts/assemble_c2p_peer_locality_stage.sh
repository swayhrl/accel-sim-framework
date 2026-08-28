#!/usr/bin/env bash
# Assemble an audited peer-locality stage from non-overlapping replay shards.
# The result root contains only symbolic links plus a provenance manifest; raw
# simulator artifacts remain in their original roots.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/assemble_c2p_peer_locality_stage.sh --manifest FILE \
       --base ROOT --extra ROOT --out ROOT [--extra-cases CASE[,CASE...]]

All manifest cases not named by --extra-cases come from --base.  The script
requires a normal simulator exit and provenance for every selected case.  It
also refuses to combine shards whose GPGPU-Sim commit, Accel-Sim commit,
compiled simulator hash, or complete configuration hash differ.
EOF
}

manifest=""
base=""
extra=""
out=""
extra_cases="atax,bicg,gesummv,3mm,gemm"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --manifest) manifest="$2"; shift 2 ;;
    --base) base="$2"; shift 2 ;;
    --extra) extra="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    --extra-cases) extra_cases="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$manifest" && -f "$manifest" ]] || { echo "error: --manifest required" >&2; exit 2; }
[[ -n "$base" && -d "$base" ]] || { echo "error: --base required" >&2; exit 2; }
[[ -n "$extra" && -d "$extra" ]] || { echo "error: --extra required" >&2; exit 2; }
[[ -n "$out" ]] || { echo "error: --out required" >&2; exit 2; }
[[ ! -e "$out" ]] || { echo "error: output already exists: $out" >&2; exit 2; }

contains_extra() {
  local wanted="$1" item
  IFS=',' read -ra items <<< "$extra_cases"
  for item in "${items[@]}"; do [[ "$item" == "$wanted" ]] && return 0; done
  return 1
}

provenance_value() {
  local file="$1" key="$2"
  awk -F= -v key="$key" '$1 == key { print substr($0, length(key) + 2); exit }' "$file"
}

mkdir -p "$out"
trap 'rm -rf "$out"' ERR
printf 'case\tsource_root\trun_dir\tgpgpusim_commit\taccelsim_commit\tconfig_sha256\ttrace_sha256\tsim_sha256\n' \
  > "$out/provenance_manifest.tsv"

reference_gpgpu=""
reference_accel=""
reference_config=""
reference_sim=""
while IFS=$'\t' read -r case _; do
  [[ -z "$case" || "$case" == case || "$case" == \#* ]] && continue
  source_root="$base"
  contains_extra "$case" && source_root="$extra"
  run_dir="$source_root/$case/oracle"
  run_out="$run_dir/run.out"
  provenance="$run_dir/provenance.txt"
  [[ -f "$run_out" && -f "$provenance" ]] || {
    echo "error: missing completed run for $case: $run_dir" >&2; exit 1;
  }
  grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_out" || {
    echo "error: $case did not exit normally: $run_dir" >&2; exit 1;
  }
  gpgpu="$(provenance_value "$provenance" gpgpusim_commit)"
  accel="$(provenance_value "$provenance" accelsim_commit)"
  config="$(provenance_value "$provenance" config_sha256)"
  trace="$(provenance_value "$provenance" trace_sha256)"
  sim="$(provenance_value "$provenance" sim_sha256)"
  [[ -n "$gpgpu" && -n "$accel" && -n "$config" && -n "$trace" && -n "$sim" ]] || {
    echo "error: incomplete provenance for $case" >&2; exit 1;
  }
  if [[ -z "$reference_gpgpu" ]]; then
    reference_gpgpu="$gpgpu"; reference_accel="$accel"
    reference_config="$config"; reference_sim="$sim"
  fi
  [[ "$gpgpu" == "$reference_gpgpu" && "$accel" == "$reference_accel" &&
     "$config" == "$reference_config" && "$sim" == "$reference_sim" ]] || {
    echo "error: shard provenance differs at $case" >&2; exit 1;
  }
  ln -s "$(realpath "$source_root/$case")" "$out/$case"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$case" "$(realpath "$source_root")" "$(realpath "$run_dir")" \
    "$gpgpu" "$accel" "$config" "$trace" "$sim" >> "$out/provenance_manifest.tsv"
done < "$manifest"

trap - ERR
echo "assembled $out"
