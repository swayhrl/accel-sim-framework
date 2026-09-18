# Source anchors

- `ldst_unit::memory_cycle()` gates translation on `!access.vm_translation_applied()`.
- `mem_access_t::set_sim_pa()` sets `m_vm_translation_applied = true`.
- `warp_inst_t::generate_mem_accesses()` creates coalesced transactions; global/local/param-local use `memory_coalescing_arch()`.
- `translate_local_memaddr()` depends on SM and CTA placement, but measured LOCAL access count did not vary.
