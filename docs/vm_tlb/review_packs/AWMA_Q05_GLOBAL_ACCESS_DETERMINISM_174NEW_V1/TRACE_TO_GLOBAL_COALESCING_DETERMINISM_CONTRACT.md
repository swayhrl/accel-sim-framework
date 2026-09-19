# Trace-to-global coalescing determinism contract

For GLOBAL trace instructions, parser-supplied active masks and lane addresses are copied before coalescing and are not rewritten by the trace shader core. `generate_mem_accesses()` is guarded by `m_mem_accesses_created`; GLOBAL uses the fixed `memory_coalescing_arch()` path. This is simulator-source semantics, not a hardware claim.
