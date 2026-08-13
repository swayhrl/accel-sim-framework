#!/usr/bin/env bash
# Archive --to-command adapter for a set of workload trace directories.
# It derives the workload root from TAR_FILENAME, then delegates the actual
# CTA/instruction filtering to the single-trace helper.
set -euo pipefail

: "${TRACE_FRACTION_CASE_OUTPUT_DIR:?}"
: "${TAR_FILENAME:?}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
delegate="$repo_root/scripts/filter_decoupled_l2_archive_trace_member.sh"
[[ -x "$delegate" ]] || { echo "error: missing $delegate" >&2; exit 2; }

case_path="${TAR_FILENAME%/traces/kernel-*.traceg}"
[[ "$case_path" != "$TAR_FILENAME" && "$case_path" != /* && "$case_path" != *".."* ]] || {
    echo "error: invalid trace member $TAR_FILENAME" >&2
    exit 2
}
case_output="$TRACE_FRACTION_CASE_OUTPUT_DIR/$case_path"
mkdir -p "$case_output/traces"

exec env TRACE_FRACTION_OUTPUT_DIR="$case_output" "$delegate"
