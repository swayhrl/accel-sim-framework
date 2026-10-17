#!/usr/bin/env bash
set -euo pipefail
o=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2/integration-debug-v3
mkdir "$o"
python3 - "$o" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=Path('rtl/ep_l2/tb/ep_l2_slice_tb.sv').read_text().replace('    reg clk=0;', '    initial begin #1;$display("DEBUG_T1");#10;$display("DEBUG_T11");#100;$display("DEBUG_T111");$finish;end\n    reg clk=0;');(p/'debug_tb.sv').write_text(s)
PY
iverilog -g2012 -s ep_l2_slice_tb -o "$o/debug.vvp" -f rtl/ep_l2/flow/full_slice_filelist.f -DEP_L2_FULL_TOP "$o/debug_tb.sv" > "$o/debug-compile.log" 2>&1
timeout 60 stdbuf -oL -eL vvp -v "$o/debug.vvp" > "$o/debug-run.log" 2>&1
