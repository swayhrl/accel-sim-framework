// Empty user callback with the same static NVBit dispatcher linkage as raw
// census.  It distinguishes user logging from NVBit core dispatch itself.

#include <stdio.h>
#include "nvbit.h"
#include "nvbit_tool.h"

using NvbitLinkAnchor = const char* (*)(CUcontext, CUfunction, bool);
__attribute__((used)) static NvbitLinkAnchor const c16_nvbit_link_anchor = &nvbit_get_func_name;

void nvbit_at_init() {
    printf("C16_EMPTY_CALLBACK_TOOL_READY callback_body=immediate_return\n");
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext, int, nvbit_api_cuda_t, const char*, void*, CUresult*) {
    return;
}

void nvbit_at_term() {
    printf("C16_EMPTY_CALLBACK_TOOL_TERMINAL\n");
    fflush(stdout);
}
