#!/usr/bin/env python3
"""Static no-GPU assertions for separate formal ROI routes and naming."""
from pathlib import Path
root=Path(__file__).resolve().parent
driver=(root/"run_m4a_c.sh").read_text(); workload=(root/"llama_tp_workload.py").read_text()
assert "--trace-region" in driver and "m4a-llama-${trace_region}" in driver and "ACTIVE_FROM_START=0" in driver
assert "cuProfilerStart" in workload and "cuProfilerStop" in workload and '{"prefill", "decode1", "decode_reuse"}' in workload
assert "model(input_ids=ids, use_cache=True)  # warmup" in workload
print("PASS ROI contract static test: separate prefill/decode1/decode_reuse routes")
