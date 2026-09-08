#!/usr/bin/env bash
# Materialize one diagnostic-only FAST64 overlay.  It changes the source-coupled
# mode candidate bound and the global lower-credit cap together; it never
# changes the production Core or a formal performance configuration.
set -euo pipefail

usage() {
  echo "usage: $0 --mode IO|OO --source-config PATH --output-config PATH --entries N --lower-cap N" >&2
  exit 2
}

mode= source_config= output_config= entries= lower_cap=
while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode) mode=${2:-}; shift 2 ;;
    --source-config) source_config=${2:-}; shift 2 ;;
    --output-config) output_config=${2:-}; shift 2 ;;
    --entries) entries=${2:-}; shift 2 ;;
    --lower-cap) lower_cap=${2:-}; shift 2 ;;
    *) usage ;;
  esac
done
case "$mode" in IO|OO) ;; *) usage ;; esac
test -r "$source_config" && test -n "$output_config" && test ! -e "$output_config"
case "$entries" in ''|*[!0-9]*) usage ;; esac
case "$lower_cap" in ''|*[!0-9]*) usage ;; esac
test "$entries" -gt 0 && test "$lower_cap" -gt 0

key="-gpgpu_dtc_l1_${mode,,}_pib_entries"
cap_key='-gpgpu_dtc_l1_lower_outstanding_cap'
test "$(grep -Fxc -- "$key 256" "$source_config")" = 1 || {
  echo "expected exactly one default $key 256" >&2; exit 1;
}
source_cap=$(grep -F -- "$cap_key " "$source_config" | tail -1 | awk '{print $2}')
case "$source_cap" in ''|*[!0-9]*) echo "source config has no numeric final lower cap" >&2; exit 1 ;; esac
# The coupled diagnostic starts from the frozen FAST64 64-SM candidate configuration,
# not from the separate high-cap negative-control overlay.
test "$source_cap" = 8192 || {
  echo "expected frozen FAST64 candidate final lower cap 8192, got $source_cap" >&2; exit 1;
}

mkdir -p "$(dirname "$output_config")"
awk -v key="$key" -v entries="$entries" -v cap_key="$cap_key" \
    -v source_cap="$source_cap" -v lower_cap="$lower_cap" '
  $0 == key " 256" { print key " " entries; next }
  $0 == cap_key " " source_cap { print cap_key " " lower_cap; next }
  { print }
' "$source_config" >"$output_config"

test "$(grep -Fxc -- "$key $entries" "$output_config")" = 1
test "$(grep -F -- "$cap_key " "$output_config" | tail -1)" = "$cap_key $lower_cap"
printf 'source_config_sha256\t%s\nmode\t%s\nsource_coupled_bound\t%s\nentries\t%s\nsource_final_lower_cap\t%s\ndiagnostic_global_lower_cap\t%s\noutput_config_sha256\t%s\n' \
  "$(sha256sum "$source_config" | awk '{print $1}')" "$mode" "$key" "$entries" \
  "$source_cap" "$lower_cap" "$(sha256sum "$output_config" | awk '{print $1}')" \
  >"$output_config.PROVENANCE.tsv"
