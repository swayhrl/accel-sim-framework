#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out_dir="${1:-$script_dir/results/yosys_control_proxy}"
mkdir -p "$out_dir"

yosys -Q -p "
  read_verilog $script_dir/rtl/c2p_control_proxy.v;
  hierarchy -check -top c2p_control_proxy;
  proc; opt; memory; opt;
  techmap; opt;
  abc -g AND,OR,XOR,XNOR,NAND,NOR;
  stat;
  write_json $out_dir/c2p_control_proxy.json;
" | tee "$out_dir/yosys_stat.log"

rg -q '=== c2p_control_proxy ===' "$out_dir/yosys_stat.log"
printf 'PASS yosys_control_proxy result_dir=%s\n' "$out_dir"
