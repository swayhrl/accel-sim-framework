#!/usr/bin/env bash
set -euo pipefail
run=${1:?a successful live run is required}
grammar=/data/c16/awma/simcompat-v1/bin/traceg_grammar_smoke
terminal=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2/util/tracer_nvbit/route_b_1771/route_b_terminal_receipt_verify.sh
src=$(find "$run/raw" -maxdepth 1 -name 'kernel-*.traceg.xz' -type f | head -n1)
work=$(mktemp -d /data/c16/awma/simcompat-v2/route_b/negative.XXXXXX)
trap 'rm -rf "$work"' EXIT
expect_reject() { if "$@" >/dev/null 2>&1; then echo "NEGATIVE_UNEXPECTED_PASS $*" >&2; exit 1; fi; }
head -c 256 "$src" > "$work/truncated.traceg.xz"
expect_reject "$grammar" "$work/truncated.traceg.xz"
xz -dc "$src" > "$work/base.traceg"
sed '0,/^insts = 16$/s//insts = 15/' "$work/base.traceg" | xz -1 -T0 -c > "$work/wrong_count.traceg.xz"
expect_reject "$grammar" "$work/wrong_count.traceg.xz"
sed '0,/LDG.E.64/s/ 8 1 / 3 1 /' "$work/base.traceg" | xz -1 -T0 -c > "$work/bad_width.traceg.xz"
expect_reject "$grammar" "$work/bad_width.traceg.xz"
grep -v '^ROUTEB_TERMINAL_COMPLETE ' "$run/lifecycle.log" > "$work/partial_terminal.log"
expect_reject "$terminal" "$work/partial_terminal.log"
sed 's/drop_count=0/drop_count=1/' "$run/lifecycle.log" > "$work/drop.log"
expect_reject "$terminal" "$work/drop.log"
sed 's/overflow_count=0/overflow_count=1/' "$run/lifecycle.log" > "$work/overflow.log"
expect_reject "$terminal" "$work/overflow.log"
echo ROUTE_B_NEGATIVE_REGRESSION_PASS
