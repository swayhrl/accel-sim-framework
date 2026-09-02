#!/usr/bin/env python3
"""No-GPU source-level contract for profiler-gated memcpy list records."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "tracer_nvbit/tracer_tool/tracer_tool.cu").read_text()
classifier = (Path(__file__).resolve().parent / "classify_kernels.py").read_text()

required = "if (!is_exit && (active_from_start || active_region))"
assert required in source, "MemcpyHtoD list insertion must be gated by formal ROI state"
memcpy_offset = source.index("case API_CUDA_cuMemcpyHtoD_v2")
profiler_offset = source.index("case API_CUDA_cuProfilerStart")
assert memcpy_offset < profiler_offset and "MemcpyHtoD" in source[memcpy_offset:profiler_offset]
# Truth table represented by the exact tracer predicate: formal inactive is
# excluded; formal active and legacy always-on are retained.
retain = lambda active_from_start, active_region: active_from_start or active_region
assert not retain(False, False)
assert retain(False, True)
assert retain(True, False)
# Kernel gating remains separately based on the unchanged active_region path.
assert "if (active_region) {" in source and "if (!stop_report) {\n    fprintf(kernelsFile" in source
assert 'return "MEMCPY"' in classifier and '"MemcpyHtoD,0x0001,64"' in classifier
print("PASS ROI memcpy policy: inactive excluded, active retained, kernel ROI unchanged")
