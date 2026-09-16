#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
commit=fb5d0bebee421a0153661239e1f7c2bc088d5c9e
wt=/home/huangrulin/workspace/worktrees/accel-sim-awma-hotfix-validator
r3=/data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z
out="$r3/hotfix_fb5d0b_admission"
trace=$(find "$r3/raw" -maxdepth 1 -type f -name 'kernel-*.traceg.xz' | head -n1)
mkdir -p "$out"
if [ ! -e "$wt" ]; then git -C "$repo" worktree add --detach "$wt" "$commit"; fi
test "$(git -C "$wt" rev-parse HEAD)" = "$commit"
git -C "$wt" status --short > "$out/hotfix_worktree_status.txt"
sha256sum "$wt/util/vm_tlb/awma/simulation/traceg_grammar_smoke.cc" "$wt/gpu-simulator/trace-parser/trace_parser.cc" > "$out/source_SHA256SUMS"
test "$(awk '/traceg_grammar_smoke.cc/{print $1}' "$out/source_SHA256SUMS")" = "dfc42e9225aa5d7a0e87fc1be8c433580c1bb687deb677c687ec70470187394c"
test "$(awk '/trace_parser.cc/{print $1}' "$out/source_SHA256SUMS")" = "9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28"
printf 'cd %s && util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh %s/traceg_grammar_smoke_fb5d0b\n' "$wt" "$out" > "$out/build_command.txt"
(cd "$wt" && util/vm_tlb/awma/simulation/build_traceg_grammar_smoke.sh "$out/traceg_grammar_smoke_fb5d0b") > "$out/build.stdout" 2> "$out/build.stderr"
sha256sum "$out/traceg_grammar_smoke_fb5d0b" > "$out/binary_SHA256SUMS"
printf '%s %s\n' "$out/traceg_grammar_smoke_fb5d0b" "$trace" > "$out/admission_command.txt"
set +e
"$out/traceg_grammar_smoke_fb5d0b" "$trace" > "$out/admission.stdout" 2> "$out/admission.stderr"
rc=$?
set -e
printf '%s\n' "$rc" > "$out/admission.returncode"
test "$rc" -eq 0
grep -q TRACEG_GRAMMAR_PASS "$out/admission.stdout"
grep -q '"LDGDEPBAR":16128' "$out/admission.stdout"
sha256sum "$trace" "$out"/admission.stdout "$out"/admission.stderr "$out"/admission.returncode > "$out/admission_SHA256SUMS"
echo HOTFIX_R3_ADMISSION_PASS
