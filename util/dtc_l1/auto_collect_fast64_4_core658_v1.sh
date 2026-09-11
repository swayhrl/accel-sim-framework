#!/usr/bin/env bash
# Future-only candidate builder.  It never promotes FAST64.4 or edits V4.
set -euo pipefail
case "${1:-}" in --watch) watch=1 ;; --once) watch=0 ;; *) echo "usage: $0 --watch|--once [--poll-seconds N]" >&2; exit 2 ;; esac
shift; poll=300
if test "${1:-}" = --poll-seconds; then poll=${2:-}; shift 2; fi
test "$#" -eq 0 && [[ "$poll" =~ ^[1-9][0-9]*$ ]] || { echo INVALID_ARGUMENTS >&2; exit 2; }
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
gen="$repo/docs/dtc_l1/fast64/generated"
root=/workspace/fast64-primary-r4-tag-identity-v2
log="$root/fast64_4_core658_candidate_v1.log"
coverage_v1="$gen/FAST64_4_IO_OO_COVERAGE_V1.tsv"
coverage_v2="$gen/FAST64_4_IO_OO_COVERAGE_V2_CORE658.tsv"
base="$gen/FAST64_3_BASE_SOURCE_REGISTRY_V4_CORE658.tsv"
registry="$gen/FAST64_4_PRIMARY_COLLECTOR_REGISTRY_V2_CORE658.tsv"
candidate="$gen/fast64_4_core658_candidate_v1"
io="$gen/fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_io_core6587238c_a1_v1.json"
oo="$gen/fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_oo_core6587238c_a1_v1.json"
emit() { printf '%s\tutc=%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" | tee -a "$log"; }
wait_or_exit() { test "$watch" = 1 || exit 0; sleep "$poll"; }
mkdir -p "$root"; exec 9>"$root/.fast64_4_core658_candidate_v1.lock"; flock -n 9 || { echo LOCK_HELD >&2; exit 1; }
while :; do
  if ! test -f "$io" || ! test -f "$oo"; then emit FAST64_4_CORE658_WAIT_2D_STRICT_OUTPUT "io=$io oo=$oo"; wait_or_exit; continue; fi
  if ! test -f "$coverage_v2"; then
    python3 "$repo/util/dtc_l1/prepare_fast64_4_core658_coverage_v2.py" --coverage-v1 "$coverage_v1" --io-summary "$io" --oo-summary "$oo" --output "$coverage_v2"
    emit FAST64_4_CORE658_COVERAGE_V2_PUBLISHED "coverage=$coverage_v2"
  fi
  if ! test -f "$registry"; then
    python3 "$repo/util/dtc_l1/prepare_fast64_4_primary_registry_v2.py" --generated-root "$gen" --base-registry "$base" --coverage "$coverage_v2" --output "$registry"
    emit FAST64_4_CORE658_REGISTRY_V2_PUBLISHED "registry=$registry"
  fi
  if ! test -e "$candidate"; then
    python3 "$repo/util/dtc_l1/collect_fast64_4_primary_matrix_v1.py" --registry "$registry" --output-dir "$candidate"
    emit FAST64_4_CORE658_CANDIDATE_COLLECTOR_PASS "candidate=$candidate"
  fi
  emit FAST64_4_CORE658_CANDIDATE_READY_NONPROMOTING "candidate=$candidate"
  exit 0
done
