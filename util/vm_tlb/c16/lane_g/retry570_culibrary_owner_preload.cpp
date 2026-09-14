// CUDA-library/module provenance observer for the one bounded Route-B owner
// resolution attempt.  It records an actual cuLibraryLoadData ->
// cuLibraryGetModule relation; it never names a DSO by kernel spelling.
#define _GNU_SOURCE
#include <cuda.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

static const char* registry_path() { return getenv("C16_NVBIT_CULIBRARY_OWNER_REGISTRY_PATH"); }
static const char* dso_for(const void* address, Dl_info* info) {
    if (address == nullptr || dladdr(address, info) == 0 || !info->dli_fname || !info->dli_fname[0]) return "UNRESOLVED";
    return info->dli_fname;
}
static void append(const char* event, const void* library, const void* module,
                   const char* caller, const char* code, CUresult result) {
    const char* out = registry_path(); if (!out) return;
    const int fd = open(out, O_WRONLY | O_CREAT | O_APPEND, 0600); if (fd < 0) return;
    dprintf(fd, "%s\t%p\t%p\t%s\t%s\t%d\n", event, library, module, caller, code, static_cast<int>(result));
    close(fd);
}

extern "C" CUresult CUDAAPI cuLibraryLoadData(CUlibrary* library, const void* code,
        CUjit_option* jit_options, void** jit_values, unsigned int jit_count,
        CUlibraryOption* library_options, void** library_values, unsigned int library_count) {
    using Fn = CUresult (CUDAAPI *)(CUlibrary*, const void*, CUjit_option*, void**, unsigned int,
                                    CUlibraryOption*, void**, unsigned int);
    static Fn real = nullptr; if (!real) real = reinterpret_cast<Fn>(dlsym(RTLD_NEXT, "cuLibraryLoadData"));
    Dl_info caller_info{}, code_info{};
    const char* caller = dso_for(__builtin_return_address(0), &caller_info);
    const char* code_owner = dso_for(code, &code_info);
    const CUresult result = real ? real(library, code, jit_options, jit_values, jit_count,
                                         library_options, library_values, library_count) : CUDA_ERROR_UNKNOWN;
    append("CULIBRARY_LOAD_DATA", library ? *library : nullptr, nullptr, caller, code_owner, result);
    return result;
}

extern "C" CUresult CUDAAPI cuLibraryGetModule(CUmodule* module, CUlibrary library) {
    using Fn = CUresult (CUDAAPI *)(CUmodule*, CUlibrary);
    static Fn real = nullptr; if (!real) real = reinterpret_cast<Fn>(dlsym(RTLD_NEXT, "cuLibraryGetModule"));
    Dl_info caller_info{}; const char* caller = dso_for(__builtin_return_address(0), &caller_info);
    const CUresult result = real ? real(module, library) : CUDA_ERROR_UNKNOWN;
    append("CULIBRARY_GET_MODULE", library, module ? *module : nullptr, caller, "UNRESOLVED", result);
    return result;
}
