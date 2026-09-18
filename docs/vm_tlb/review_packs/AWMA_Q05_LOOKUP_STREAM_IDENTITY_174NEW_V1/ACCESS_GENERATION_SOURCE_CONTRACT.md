# Access generation source contract

`exec_shader_core_ctx::func_exec_inst()` calls `generate_mem_accesses()`. GLOBAL, LOCAL, and PARAM_LOCAL choose the common coalescing path. Local timing addresses are mapped before coalescing by `translate_local_memaddr()`. The observed matrix holds dynamic instructions, active lanes, and LOCAL transactions fixed; only GLOBAL generated transactions vary.
