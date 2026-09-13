// Diagnostic-only NVBit 1.8 process control.
//
// It must stay deliberately empty: no instrumentation, no NVBit instruction
// enumeration, no function-name lookup, and no CUDA launch filtering.  Its
// only purpose is to distinguish generic full-model NVBit process overhead
// from the targeted mapper's work.

#include <stdio.h>

#include "nvbit_tool.h"

void nvbit_at_init() {
    printf("C16_NVBIT_NOOP_TOOL_READY no_instrumentation=1 no_instr_enumeration=1 no_function_lookup=1\n");
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext, int, nvbit_api_cuda_t, const char*, void*, CUresult*) {
    // Intentional immediate return for every CUDA event.
}

void nvbit_at_ctx_term(CUcontext) {
    printf("C16_NVBIT_NOOP_TOOL_TERMINAL\n");
    fflush(stdout);
}
