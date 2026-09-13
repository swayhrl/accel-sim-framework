// Fixed-POD callback census.  No callback path may allocate, name a CUDA API,
// touch Function objects, query NVBit, or perform instrumentation.

#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#include "nvbit.h"
#include "nvbit_tool.h"

using NvbitLinkAnchor = const char* (*)(CUcontext, CUfunction, bool);
__attribute__((used)) static NvbitLinkAnchor const c16_nvbit_link_anchor = &nvbit_get_func_name;

#pragma pack(push, 1)
struct RawHeader {
    char magic[16];
    uint32_t version;
    uint32_t event_size;
    uint64_t capacity;
    uint64_t write_count;
    uint64_t dropped_count;
    uint64_t max_callback_depth;
    uint64_t reentrant_callback_count;
};
struct RawEvent {
    uint64_t sequence;
    uint64_t timestamp_ns;
    uint64_t tid;
    uint32_t cbid;
    uint32_t is_exit;
};
#pragma pack(pop)

static constexpr uint64_t kCapacity = 65536;
static int raw_fd = -1;
static RawHeader* header = nullptr;
static RawEvent* events = nullptr;
static thread_local uint32_t callback_depth = 0;

static uint64_t monotonic_ns() {
    struct timespec value;
    clock_gettime(CLOCK_MONOTONIC, &value);
    return static_cast<uint64_t>(value.tv_sec) * 1000000000ULL + value.tv_nsec;
}

static void update_max_depth(uint64_t value) {
    uint64_t observed = __atomic_load_n(&header->max_callback_depth, __ATOMIC_RELAXED);
    while (observed < value && !__atomic_compare_exchange_n(&header->max_callback_depth, &observed, value, false, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) {}
}

void nvbit_at_init() {
    const char* path = getenv("C16_CALLBACK_CENSUS_RAW_PATH");
    if (path == nullptr || path[0] == '\0') {
        fprintf(stderr, "C16_CALLBACK_CENSUS_RAW_CONFIG_ERROR missing fixed event-buffer path\n");
        return;
    }
    raw_fd = open(path, O_CREAT | O_EXCL | O_RDWR, 0600);
    const size_t bytes = sizeof(RawHeader) + kCapacity * sizeof(RawEvent);
    if (raw_fd < 0 || ftruncate(raw_fd, static_cast<off_t>(bytes)) != 0) {
        fprintf(stderr, "C16_CALLBACK_CENSUS_RAW_CONFIG_ERROR cannot allocate fixed event buffer\n");
        return;
    }
    void* view = mmap(nullptr, bytes, PROT_READ | PROT_WRITE, MAP_SHARED, raw_fd, 0);
    if (view == MAP_FAILED) {
        fprintf(stderr, "C16_CALLBACK_CENSUS_RAW_CONFIG_ERROR cannot map fixed event buffer\n");
        return;
    }
    memset(view, 0, bytes);
    header = static_cast<RawHeader*>(view);
    events = reinterpret_cast<RawEvent*>(header + 1);
    memcpy(header->magic, "C16RAWCBV1", 10);
    header->version = 1;
    header->event_size = sizeof(RawEvent);
    header->capacity = kCapacity;
    printf("C16_CALLBACK_CENSUS_RAW_TOOL_READY capacity=%llu event_size=%u\n", static_cast<unsigned long long>(kCapacity), static_cast<unsigned>(sizeof(RawEvent)));
    fflush(stdout);
}

void nvbit_at_cuda_event(CUcontext, int is_exit, nvbit_api_cuda_t cbid, const char*, void*, CUresult*) {
    // The only callback work is a write to this preallocated POD ring.
    if (header == nullptr || events == nullptr) return;
    const uint32_t depth = ++callback_depth;
    update_max_depth(depth);
    if (depth > 1) __atomic_fetch_add(&header->reentrant_callback_count, 1ULL, __ATOMIC_RELAXED);
    const uint64_t sequence = __atomic_fetch_add(&header->write_count, 1ULL, __ATOMIC_RELAXED);
    if (sequence < header->capacity) {
        events[sequence] = RawEvent{sequence, monotonic_ns(), static_cast<uint64_t>(syscall(SYS_gettid)), static_cast<uint32_t>(cbid), static_cast<uint32_t>(is_exit)};
    } else {
        __atomic_fetch_add(&header->dropped_count, 1ULL, __ATOMIC_RELAXED);
    }
    --callback_depth;
}

void nvbit_at_term() {
    if (header != nullptr) {
        const size_t bytes = sizeof(RawHeader) + kCapacity * sizeof(RawEvent);
        msync(header, bytes, MS_SYNC);
        munmap(header, bytes);
        header = nullptr;
        events = nullptr;
    }
    if (raw_fd >= 0) close(raw_fd);
    printf("C16_CALLBACK_CENSUS_RAW_TOOL_TERMINAL\n");
    fflush(stdout);
}
