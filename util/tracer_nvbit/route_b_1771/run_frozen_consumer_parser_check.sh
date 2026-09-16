#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
frozen=25aa29862239a408099639ae9d5f1a0ea4fee1e1
wt=/home/huangrulin/workspace/worktrees/accel-sim-awma-consumer25-checkpoint
out=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z/frozen_consumer25
trace=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z/raw/kernel-34-ctx_0x56f950199aa0.traceg.xz
mkdir -p "$out"
git -C "$repo" fetch origin
git -C "$repo" cat-file -e "${frozen}^{commit}"
if [ ! -e "$wt" ]; then
  git -C "$repo" worktree add --detach "$wt" "$frozen"
fi
test "$(git -C "$wt" rev-parse HEAD)" = "$frozen"
git -C "$wt" status --short > "$out/frozen_worktree_status.txt"
sha256sum "$wt/util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc" "$wt/gpu-simulator/trace-parser/trace_parser.cc" > "$out/parser_source_SHA256SUMS"
cmd="cd $wt && util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh $out/traceg_grammar_smoke_25aa"
printf '%s\n' "$cmd" > "$out/build_command.txt"
(cd "$wt" && util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh "$out/traceg_grammar_smoke_25aa") > "$out/build.stdout" 2> "$out/build.stderr"
sha256sum "$out/traceg_grammar_smoke_25aa" > "$out/parser_binary_SHA256SUMS"
printf '%s\n' "$out/traceg_grammar_smoke_25aa $trace" > "$out/run_command.txt"
set +e
"$out/traceg_grammar_smoke_25aa" "$trace" > "$out/parser.stdout" 2> "$out/parser.stderr"
rc=$?
set -e
printf '%s\n' "$rc" > "$out/parser.returncode"
sha256sum "$trace" > "$out/traceg_input_SHA256SUMS"
printf 'frozen_commit=%s\n' "$frozen" > "$out/frozen_commit.txt"
echo FROZEN_CONSUMER_PARSER_CHECK_DONE rc="$rc"
