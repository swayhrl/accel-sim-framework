# C16 E1 targeted CUDA L2-persistence interpretation

Final scoped state: `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`.

Local CUDA headers/runtime and the RTX4080 independently qualify persisting-L2 control. Exact layer0/layer14 up_proj and layer0 down_proj qweight tensors are separate contiguous 33,947,648-byte intervals. CUDA rounds the full requested qweight set-aside to 37,748,736 bytes; every condition records and resets this runtime state.

The isolated positive control demonstrates policy effectiveness: exact qweight persistence reduces isolated dense-pressure target timing and DRAM substantially without changing semantic identity. Under natural full-model decode, target persistence produces material, target-specific timing benefits at stable D1/D3 occurrences for up_proj and D3 for down_proj. Set-aside-only and matched unrelated-persistence controls are kept separate. Natural DRAM generally improves, but the L0 up D3 target reduction is just below the preregistered 20% gate and matched unrelated persistence can reduce DRAM as much or more; traffic is therefore not claimed target-specific.

Budget sensitivity finds the first tested material L0 up D3 timing benefit at `16MIB` while keeping the full qweight window and scaling hitRatio. No tested budget meets the preregistered DRAM material gate, and no exact threshold is claimed.

The evidence supports abstract design-review requirements for selective qweight-like residency across inter-token reuse, but it does not select or implement a classifier, replacement policy, cache/TLB mechanism, or simulator change. No NVBit or full address trace was started.
