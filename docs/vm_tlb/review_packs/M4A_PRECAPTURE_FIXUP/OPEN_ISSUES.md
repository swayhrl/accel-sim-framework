# Open issues and stop boundary

1. The paper's exact TP implementation, dtype, model revision, contiguous
   loader, and treatment of collective kernels remain unavailable.
2. Route E needs a matching 4 x SM86 node and an M4A-C authorization. The
   frozen tracer's rank0-only behavior must first pass a tiny tracer smoke.
3. Route A has not been approved and no full-model fallback is permitted.
4. Runtime flat-buffer binding validates virtual storage identity only; GPU
   physical contiguity and trace-address coverage remain M4A-C checks.

STOP. Do not rent, trace, implement Segmentation, or inject synthetic KV.
