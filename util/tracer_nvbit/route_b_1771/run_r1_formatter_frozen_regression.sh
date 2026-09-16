#!/usr/bin/env bash
set -euo pipefail
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
bin=/data/c16/awma/simcompat-v2/route_b/bin/route_b_formatter_selftest
frozen=/data/c16/awma/simcompat-v2/q05_routeb_canary_r3_20260917T0110Z/frozen_consumer25/traceg_grammar_smoke_25aa
post="$repo/util/tracer_nvbit/tracer_tool/traces-processing/post-traces-processing"
out=/data/c16/awma/simcompat-v2/formatter_frozen_regression_20260917
mkdir -p "$out/raw"
"$bin" > "$out/selftest.stdout"
"$bin" --emit-raw > "$out/raw/records.raw"
cat > "$out/raw/kernel-1.trace" <<'EOF'
-kernel name = r1_formatter_frozen_regression
-kernel id = 1
-grid dim = (1,1,1)
-block dim = (32,1,1)
-shmem = 0
-nregs = 8
-binary version = 89
-cuda stream id = 0
-shmem base_addr = 0x0
-local mem base_addr = 0x0
-nvbit version = 1.7.7.1
-accelsim tracer version = 5
-enable lineinfo = 0

#traces format = [line_num] PC mask dest_num [reg_dests] opcode src_num [reg_srcs] mem_width [addresscompress?] [mem_addresses] immediate

EOF
cat "$out/raw/records.raw" >> "$out/raw/kernel-1.trace"
printf 'kernel-1.trace\n' > "$out/raw/kernelslist"
"$post" "$out/raw" > "$out/postprocess.stdout" 2> "$out/postprocess.stderr"
"$frozen" "$out/raw/kernel-1.traceg" > "$out/frozen_parser.stdout" 2> "$out/frozen_parser.stderr"
grep -q ROUTE_B_FORMATTER_SELFTEST_PASS "$out/selftest.stdout"
grep -q TRACEG_GRAMMAR_PASS "$out/frozen_parser.stdout"
if grep -Eq '^[0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9a-f]+ [0-9a-f]+ [0-9]+( R[0-9]+)* [^ ]+ [0-9]+( R[0-9]+)* [0-9]+ 2 ' "$out/raw/kernel-1.trace"; then
  echo R1_MODE2_UNEXPECTED >&2
  exit 1
fi
sha256sum "$out/raw/kernel-1.trace" "$out/raw/kernel-1.traceg" "$out/raw/kernelslist" "$out/raw/kernelslist.g" "$out/selftest.stdout" "$out/frozen_parser.stdout" > "$out/SHA256SUMS"
echo R1_FORMATTER_FROZEN_REGRESSION_PASS
