# Wrapper gate — not entered

The required `recall@10>=0.95` gate failed before formal Q1 timing. The screen used device-resident queries and preallocated neighbor/distance output arrays, but its preliminary host timings cannot distinguish Python wrapper/allocations from GPU search work. No NSYS attribution, C/C++ preallocated fallback or persistent control was run. Therefore neither `R17_HOST_OR_WRAPPER_DOMINANT` nor a GPU-local residual can be claimed. The correct primary label is the earlier quality failure.
