#!/usr/bin/env bash
# Create an isolated FAST64 diagnostic overlay.  In the current Core source the
# lower-create candidate-queue bound is deliberately coupled to the mode PIB
# setting; this tool changes that one source-backed bound, never the global cap.
set -euo pipefail

usage() {
  echo "usage: $0 --mode IO|OO --source-config PATH --output-config PATH --entries N" >&2
  exit 2
}

mode=
source_config=
output_config=
entries=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode) mode=${2:-}; shift 2 ;;
    --source-config) source_config=${2:-}; shift 2 ;;
    --output-config) output_config=${2:-}; shift 2 ;;
    --entries) entries=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done

case "$mode" in IO|OO) ;; *) usage ;; esac
test -r "$source_config"
test -n "$output_config"
test ! -e "$output_config"
case "$entries" in ''|*[!0-9]*) usage ;; esac
test "$entries" -gt 0

key="-gpgpu_dtc_l1_${mode,,}_pib_entries"
test "$(grep -Fxc -- "$key 256" "$source_config")" = 1 || {
  echo "expected exactly one default $key 256" >&2; exit 1;
}
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$source_config" | tail -1)" = \
  '-gpgpu_dtc_l1_lower_outstanding_cap 1048576' || {
  echo "source config final lower cap is not high/non-binding" >&2; exit 1;
}

mkdir -p "$(dirname "$output_config")"
awk -v key="$key" -v entries="$entries" '
  $0 == key " 256" { print key " " entries; next }
  { print }
' "$source_config" >"$output_config"

test "$(grep -Fxc -- "$key $entries" "$output_config")" = 1
test "$(grep -F -- '-gpgpu_dtc_l1_lower_outstanding_cap ' "$output_config" | tail -1)" = \
  '-gpgpu_dtc_l1_lower_outstanding_cap 1048576'
printf 'source_config_sha256\t%s\nmode\t%s\nsource_coupled_bound\t%s\nentries\t%s\noutput_config_sha256\t%s\n' \
  "$(sha256sum "$source_config" | awk '{print $1}')" "$mode" "$key" "$entries" \
  "$(sha256sum "$output_config" | awk '{print $1}')" \
  >"$output_config.PROVENANCE.tsv"
