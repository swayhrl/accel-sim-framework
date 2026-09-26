# Source and closest-work audit

- Background semantics are closed by an exact hook on `model.get_output_embeddings()` at accepted Qwen S2 decode step16; the replay selects the same `internal::gemvx` grid `18992,1,1`, block `8,8,1` that was previously only an UNKNOWN-role clue.
- Foreground reuses the accepted P1 layer-12 Flash-SDPA B1 tensors/output without contract drift.
- CUDA exposes priority range low `0` to high `-5`; distinct streams and NSYS stream IDs are recorded.
- LithOS kernel atomization, GPREEMPT driver timeslicing, ExpertPlex cooperative tile handoff, MPK task graphs, and PipeThreader reduction/pipeline decomposition are the closest software/system capabilities in Round-05 (`d6a10f02...`). This stage does not claim a residual against them because its own required strong software baseline failed the exact output gate.
- No driver change, general scheduler, hardware mechanism, model download, NCU, NVBit full trace, Accel-Sim, or node174 task was used.
