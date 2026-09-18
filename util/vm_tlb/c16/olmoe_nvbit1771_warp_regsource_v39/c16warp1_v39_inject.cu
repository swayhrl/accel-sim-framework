#include <stdint.h>
#include <limits.h>

#include "utils/channel.hpp"
#include "utils/utils.h"
#include "c16warp1_v39_common.h"

// The helper runs once logically per predicated warp: all participating lanes
// form the V20 mask/gather and the first participating lane pushes one packet.
extern "C" __device__ __noinline__ void c16warp1_record_mref(
    int pred, uint64_t addr, uint32_t static_index, uint64_t counter_ptr,
    uint64_t capacity, uint64_t packed_cta_range, uint64_t channel_ptr) {
    const int cta_begin = (int)(packed_cta_range >> 32);
    const int cta_end = (int)(packed_cta_range & 0xffffffffu);
    // Match the official 1.7.7.1 helper's guarded-callback discipline.  NVBit
    // calls this helper under the original instruction predicate; do not make a
    // ballot whose predicate spans lanes that did not enter the callback.
    if (!pred) return;
    unsigned mask = __ballot_sync(__activemask(), 1);
    if ((int)blockIdx.x < cta_begin || (int)blockIdx.x >= cta_end) return;
    unsigned lane = threadIdx.x & 31;
    uint64_t gathered[32];
    for (int i = 0; i < 32; ++i) gathered[i] = __shfl_sync(mask, addr, i);
    if (lane != (unsigned)(__ffs(mask) - 1)) return;

    c16warp1_device_counters_t* ctr = (c16warp1_device_counters_t*)counter_ptr;
    const unsigned long long sequence = atomicAdd(&ctr->producer_records, 1ULL);
    if (sequence >= capacity) {
        atomicAdd(&ctr->producer_overflow, 1ULL);
        return;
    }
    // ChannelDev provides byte-integrity but concurrent warps may otherwise
    // enter its push path in a different order from the sequence-ticket atomic.
    // Gate admission by ticket so receiver order is independently auditable.
    while (atomicAdd(&ctr->producer_next_to_push, 0ULL) != sequence) {}
    c16warp1_packet_t packet{};
    packet.sequence = sequence;
    packet.record.static_index = static_index;
    packet.record.active_mask = mask;
    packet.record.cta_x = blockIdx.x;
    packet.record.cta_y = blockIdx.y;
    packet.record.cta_z = blockIdx.z;
    packet.record.warp = get_warpid();
    for (int i = 0; i < 32; ++i) packet.record.addr[i] = gathered[i];
    ((ChannelDev*)channel_ptr)->push(&packet, sizeof(packet));
    __threadfence_system();
    atomicAdd(&ctr->producer_next_to_push, 1ULL);
}

extern "C" __device__ __noinline__ void c16warp1_record_reg(
    int pred, uint32_t lo, uint32_t hi, uint32_t static_index,
    uint64_t counter_ptr, uint64_t capacity, uint64_t packed_cta_range,
    uint64_t channel_ptr) {
    c16warp1_record_mref(pred, ((uint64_t)hi << 32) | lo, static_index, counter_ptr,
                         capacity, packed_cta_range, channel_ptr);
}

// --keep-device-functions in the tool-patch compilation rule retains both
// callbacks for NVBit symbol resolution.  This translation unit must not also
// declare a kernel entry point: ptxas rejects entries in a tools-patch object.
