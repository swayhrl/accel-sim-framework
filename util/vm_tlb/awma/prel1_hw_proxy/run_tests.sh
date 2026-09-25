#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out="$here/out/tests"
mkdir -p "$out"

run_case() {
  local name=$1
  local registered=$2
  local waiter_width=$3
  iverilog -g2012 -s prel1_exact_coalescer_proxy_tb \
    -Pprel1_exact_coalescer_proxy_tb.REGISTER_COMPARE="$registered" \
    -Pprel1_exact_coalescer_proxy_tb.WAITER_META_W="$waiter_width" \
    -o "$out/$name.vvp" \
    "$here/prel1_exact_coalescer_proxy.v" \
    "$here/prel1_exact_coalescer_proxy_tb.v"
  vvp "$out/$name.vvp" >"$out/$name.log" 2>&1
  grep -q "PREL1_RTL_PROXY_TEST PASS registered=$registered waiter_meta=$waiter_width" \
    "$out/$name.log"
}

run_case same_cycle_minimal 0 32
run_case registered_minimal 1 32
run_case same_cycle_conservative 0 325
run_case registered_conservative 1 325
sha256sum "$out"/*.log >"$out/SHA256SUMS"
echo RTL_TESTS_PASS
