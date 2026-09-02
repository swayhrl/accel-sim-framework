# Open issues and stop boundary

1. No public author artifact, exact Llama trace, TP=4 capture method, dtype,
   sub-entry design, PTW model, synthetic-KV distribution, or contiguous
   loader was found.  These are recorded as `PAPER_DETAIL_UNAVAILABLE`; no
   approximation is claimed or implemented.
2. A target SM86 rental host, its driver/CUDA compatibility, and measured trace
   growth remain intentionally unselected / unmeasured.
3. The fresh host must build and smoke the frozen tracer before LLM work.
4. The runtime command must provide a real allocator hook and sidecar; static
   layout validation does not prove GPU virtual-address contiguity.

STOP: M4A-P ends here.  Do not invoke the external capture driver, rent a GPU,
collect a trace, implement Segmentation, or inject synthetic KV traffic without
a new authorization recorded in `chatgpt_handoff`.
