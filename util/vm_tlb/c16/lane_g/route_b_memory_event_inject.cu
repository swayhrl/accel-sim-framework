#include <stdint.h>
#include "route_b_memory_event_common.h"

// One callback invocation represents one executing lane.  The host tool must
// bind this symbol only to a sorted (static_index,mref_ordinal) whitelist whose
// static map declares GLOBAL && has_mref and an explicit mref_count.
extern "C" __device__ __noinline__ void route_b_append_memory_event(
    int predicate, uint64_t address, uint64_t launch_id, uint32_t static_index,
    uint32_t mref_ordinal, uint32_t instruction_offset, uint32_t width_bytes,
    uint32_t access_kind, uint64_t buffer_address) {
    RouteBBuffer* buffer = reinterpret_cast<RouteBBuffer*>(buffer_address);
    const uint32_t active = __activemask();
    const uint32_t predicate_mask = __ballot_sync(active, predicate != 0);
    const uint32_t executing = active & predicate_mask;
    const uint32_t lane = threadIdx.x & 31;
    if ((executing & (1U << lane)) == 0) return;
    if (address == 0) { atomicAdd(&buffer->drop_count, 1ULL); return; }
    const uint64_t slot = atomicAdd(&buffer->next_sequence, 1ULL);
    if (slot >= buffer->capacity) { atomicAdd(&buffer->overflow_count, 1ULL); return; }
    RouteBEventRecord* event = &buffer->records[slot];
    event->observed_callback_sequence = slot;
    event->launch_id = launch_id; event->address = address;
    event->static_index = static_index; event->mref_ordinal = mref_ordinal;
    event->cta_x = blockIdx.x; event->cta_y = blockIdx.y; event->cta_z = blockIdx.z;
    event->warp_id = ((threadIdx.z * blockDim.y + threadIdx.y) * blockDim.x + threadIdx.x) >> 5;
    event->active_mask = active; event->predicate_mask = predicate_mask;
    event->executing_mask = executing; event->address_lane = lane;
    event->instruction_offset = instruction_offset; event->width_bytes = width_bytes;
    event->access_kind = access_kind;
    __threadfence_system();
}
