// CUDA-runtime registration provenance for Route-B V2 map-only diagnostics.
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static const char* registry_path() { return getenv("C16_NVBIT_FATBIN_OWNER_REGISTRY_PATH"); }
static void write_owner(const char* device, const void* host) {
    const char* out = registry_path(); if (!out || !device || !device[0]) return;
    Dl_info info{}; if (host == nullptr || dladdr(host, &info) == 0 || !info.dli_fname) return;
    int fd = open(out, O_WRONLY | O_CREAT | O_APPEND, 0600); if (fd < 0) return;
    dprintf(fd, "%s\t%s\n", device, info.dli_fname); close(fd);
}
extern "C" void** __cudaRegisterFatBinary(void* fat) {
    using Fn = void** (*)(void*); static Fn real = nullptr;
    if (!real) real = reinterpret_cast<Fn>(dlsym(RTLD_NEXT, "__cudaRegisterFatBinary"));
    return real ? real(fat) : nullptr;
}
extern "C" void __cudaRegisterFunction(void** h, const char* host, char* device, const char* name,
                                         int limit, void* tid, void* bid, void* bdim, void* gdim, int* wsize) {
    using Fn = void (*)(void**, const char*, char*, const char*, int, void*, void*, void*, void*, int*);
    static Fn real = nullptr;
    if (!real) real = reinterpret_cast<Fn>(dlsym(RTLD_NEXT, "__cudaRegisterFunction"));
    write_owner(device, host);
    if (real) real(h, host, device, name, limit, tid, bid, bdim, gdim, wsize);
}
