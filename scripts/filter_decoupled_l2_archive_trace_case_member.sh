#!/usr/bin/env bash
# Archive --to-command adapter for a set of workload trace directories.
# It derives the workload root from TAR_FILENAME, then delegates the actual
# CTA/instruction filtering to the single-trace helper.
set -euo pipefail

: "${TRACE_FRACTION_CASE_OUTPUT_DIR:?}"
: "${TAR_FILENAME:?}"
min_free_kib="${TRACE_FRACTION_MIN_FREE_KIB:-0}"
[[ "$min_free_kib" =~ ^[0-9]+$ ]] || {
    echo "error: invalid TRACE_FRACTION_MIN_FREE_KIB=$min_free_kib" >&2
    exit 2
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
delegate="$repo_root/scripts/filter_decoupled_l2_archive_trace_member.sh"
[[ -x "$delegate" ]] || { echo "error: missing $delegate" >&2; exit 2; }

case_path="${TAR_FILENAME%/traces/kernel-*.traceg}"
[[ "$case_path" != "$TAR_FILENAME" && "$case_path" != /* && "$case_path" != *".."* ]] || {
    echo "error: invalid trace member $TAR_FILENAME" >&2
    exit 2
}
case_output="$TRACE_FRACTION_CASE_OUTPUT_DIR/$case_path"
# The archive is streamed, but each selected kernel becomes a real output
# file.  Check immediately before creating it so batch preparation cannot
# consume the experiment's required disk reserve.
free_kib="$(df -Pk "$TRACE_FRACTION_CASE_OUTPUT_DIR" | awk 'NR == 2 { print $4 }')"
if (( free_kib < min_free_kib )); then
    printf 'error: free space %s KiB is below reserve %s KiB before %s\n' \
        "$free_kib" "$min_free_kib" "$TAR_FILENAME" >&2
    exit 1
fi
mkdir -p "$case_output/traces"

exec env TRACE_FRACTION_OUTPUT_DIR="$case_output" "$delegate"
