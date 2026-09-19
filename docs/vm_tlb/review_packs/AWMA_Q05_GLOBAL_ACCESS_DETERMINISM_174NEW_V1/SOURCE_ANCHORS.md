# Source anchors

- `trace_parser::get_next_threadblock_traces()` consumes trace warp vectors in CTA order.
- `trace_shd_warp_t::get_next_trace_inst()` copies one immutable trace record at `trace_pc`.
- `trace_warp_inst_t::parse_from_trace_struct()` copies PC, active mask and decompressed lane addresses.
- `trace_shader_core_ctx::checkExecutionStatusAndUpdate()` rewrites only LOCAL addresses.
- `trace_shader_core_ctx::func_exec_inst()` invokes `generate_mem_accesses()` synchronously.
