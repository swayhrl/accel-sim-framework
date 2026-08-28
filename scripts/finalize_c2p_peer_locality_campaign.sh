#!/usr/bin/env bash
# Wait for the non-overlapping C2P peer-locality shards, then assemble and
# audit them without copying the simulator artifacts.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/finalize_c2p_peer_locality_campaign.sh --root CAMPAIGN_ROOT
       [--poll-sec N]

The campaign root must contain current64, current64-extra, literal16k, and
fourset64k.  The current64-extra shard supplies atax/bicg/gesummv/3mm/gemm;
the canonical current64 root supplies the other eleven paper16 cases.

The command waits without modifying live run directories.  Once every valid
cell exits normally, it validates shard provenance, makes a link-only
assembled stage, audits all three stages, and writes cross-stage CSVs under
CAMPAIGN_ROOT/analysis.  Literal-16KiB Gaussian is accepted only as the
documented invalid baseline-deadlock cell.
EOF
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
root=""
poll_sec=60
while [[ $# -gt 0 ]]; do
  case "$1" in
    --root) root="$2"; shift 2 ;;
    --poll-sec) poll_sec="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$root" && -d "$root" ]] || { echo "error: --root must exist" >&2; exit 2; }
[[ "$poll_sec" =~ ^[1-9][0-9]*$ ]] || { echo "error: --poll-sec must be positive" >&2; exit 2; }

manifest="$repo_root/configs/c2p-cache/paper16_workloads.tsv"
base_cases="btree,dwt2d,gaussian,hotspot1,lud,nn,cutcp,mri-q,sgemm,stencil,2DConvolution"
extra_cases="atax,bicg,gesummv,3mm,gemm"
geometry_cases="hotspot1,gaussian,lud,sgemm,3mm,gemm"
literal_valid_cases="hotspot1,lud,sgemm,3mm,gemm"

split_cases() { tr ',' '\n' <<< "$1"; }
normal_exit() {
  local run_out="$1/$2/oracle/run.out"
  [[ -f "$run_out" ]] && grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$run_out"
}
unexpected_failure() {
  local run_out="$1/$2/oracle/run.out"
  [[ -f "$run_out" ]] &&
    grep -q 'GPGPU-Sim uArch: ERROR\|deadlock detected' "$run_out"
}
all_normal() {
  local stage="$1" cases="$2" case
  while read -r case; do normal_exit "$stage" "$case" || return 1; done \
    < <(split_cases "$cases")
}
assert_no_unexpected_failure() {
  local stage="$1" cases="$2" allowed_fail="${3:-}" case
  while read -r case; do
    [[ "$case" == "$allowed_fail" ]] || ! unexpected_failure "$stage" "$case" || {
      echo "error: unexpected failed cell: $stage/$case" >&2; return 1;
    }
  done < <(split_cases "$cases")
}

for stage in current64 current64-extra literal16k fourset64k; do
  [[ -d "$root/$stage" ]] || { echo "error: missing stage root $stage" >&2; exit 2; }
done

while :; do
  assert_no_unexpected_failure "$root/current64" "$base_cases"
  assert_no_unexpected_failure "$root/current64-extra" "$extra_cases"
  assert_no_unexpected_failure "$root/literal16k" "$geometry_cases" gaussian
  assert_no_unexpected_failure "$root/fourset64k" "$geometry_cases"
  literal_deadlock="$root/literal16k/gaussian/oracle/run.out"
  if all_normal "$root/current64" "$base_cases" &&
     all_normal "$root/current64-extra" "$extra_cases" &&
     all_normal "$root/literal16k" "$literal_valid_cases" &&
     all_normal "$root/fourset64k" "$geometry_cases" &&
     [[ -f "$literal_deadlock" ]] && grep -q 'deadlock detected' "$literal_deadlock"; then
    break
  fi
  echo "[$(date -Is)] waiting for qualified peer-locality cells"
  sleep "$poll_sec"
done

assembled_current="$root/current64-assembled"
assembled_root="$root/assembled-campaign"
[[ ! -e "$assembled_current" && ! -e "$assembled_root" ]] || {
  echo "error: assembled output already exists; refusing overwrite" >&2; exit 2;
}
"$repo_root/scripts/assemble_c2p_peer_locality_stage.sh" \
  --manifest "$manifest" --base "$root/current64" --extra "$root/current64-extra" \
  --out "$assembled_current" --extra-cases "$extra_cases"

python3 "$repo_root/scripts/analyze_c2p_peer_locality.py" \
  --manifest "$manifest" --root "current64=$assembled_current" \
  --out-dir "$assembled_current/analysis"
python3 "$repo_root/scripts/analyze_c2p_peer_locality.py" \
  --manifest "$manifest" --case "$literal_valid_cases" \
  --root "literal16k=$root/literal16k" --out-dir "$root/literal16k/analysis"
printf 'case,status,reason\ngaussian,INVALID_BASELINE_DEADLOCK,documented literal-16KiB baseline deadlock\n' \
  > "$root/literal16k/analysis/invalid_geometry_cases.csv"
python3 "$repo_root/scripts/analyze_c2p_peer_locality.py" \
  --manifest "$manifest" --case "$geometry_cases" \
  --root "fourset64k=$root/fourset64k" --out-dir "$root/fourset64k/analysis"

mkdir "$assembled_root"
ln -s "$(realpath "$assembled_current")" "$assembled_root/current64"
ln -s "$(realpath "$root/literal16k")" "$assembled_root/literal16k"
ln -s "$(realpath "$root/fourset64k")" "$assembled_root/fourset64k"
python3 "$repo_root/scripts/summarize_c2p_peer_locality.py" \
  --root "$assembled_root" --out-dir "$root/analysis" \
  --literal16k-invalid-case gaussian
echo "[$(date -Is)] finalized peer-locality campaign: $root/analysis"
