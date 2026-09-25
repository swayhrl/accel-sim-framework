#!/usr/bin/env bash
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
out="$here/out/synthesis"
mkdir -p "$out"

run_case() {
  local name=$1
  local registered=$2
  local waiter_width=$3
  local script="$out/$name.ys"
  printf '%s\n' \
    "read_verilog -sv $here/prel1_exact_coalescer_proxy.v" \
    "chparam -set REGISTER_COMPARE $registered -set WAITER_META_W $waiter_width prel1_exact_coalescer_proxy" \
    "synth -top prel1_exact_coalescer_proxy" \
    "tee -o $out/$name.stat.txt stat" \
    "tee -o $out/$name.ltp.txt ltp -noff" \
    "write_verilog -noattr $out/$name.netlist.v" >"$script"
  yosys -Q -s "$script" >"$out/$name.log" 2>&1
}

run_case same_cycle_minimal 0 32
run_case registered_minimal 1 32
run_case same_cycle_conservative 0 325
run_case registered_conservative 1 325
sha256sum "$out"/*.stat.txt "$out"/*.ltp.txt "$out"/*.netlist.v \
  >"$out/SHA256SUMS"
echo GENERIC_SYNTHESIS_PASS
