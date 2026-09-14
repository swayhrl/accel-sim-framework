#include <stdint.h>
#include "nvbit_tool.h"
#include "route_b_memory_event_common.h"

// CUDA exposes the 64-bit atomic overload as unsigned long long*. On this
// Linux ABI uint64_t is unsigned long, so adapt only at the intrinsic boundary
// while preserving the Route-B wire/layout contract as uint64_t.
static __device__ __forceinline__ uint64_t route_b_atomic_add_u64(
    uint64_t* address, uint64_t value) {
    return static_cast<uint64_t>(atomicAdd(
        reinterpret_cast<unsigned long long*>(address),
        static_cast<unsigned long long>(value)));
}

// One callback invocation produces one explicit LANE_EVENT, never a
// whole-warp address array.  The explicit instance id below prevents the host
// parser from guessing dynamic warp-instruction boundaries from adjacent atomic
// sequence numbers.  The host tool binds this only to a sorted
// (static_index,mref_ordinal) whitelist whose map declares GLOBAL && has_mref.
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
    const int leader_lane = __ffs(executing) - 1;
    uint64_t instance = 0;
    if (static_cast<int>(lane) == leader_lane) {
        instance = route_b_atomic_add_u64(&buffer->next_warp_instruction_instance, 1);
    }
    instance = __shfl_sync(executing, instance, leader_lane);
    if (address == 0) { route_b_atomic_add_u64(&buffer->drop_count, 1); return; }
    const uint64_t slot = route_b_atomic_add_u64(&buffer->next_sequence, 1);
    if (slot >= buffer->capacity) { route_b_atomic_add_u64(&buffer->overflow_count, 1); return; }
    RouteBLaneEvent* event = &buffer->records[slot];
    event->observed_callback_sequence = slot;
    event->warp_instruction_instance_id = instance;
    event->launch_id = launch_id; event->gpu_va = address;
    event->static_index = static_index; event->mref_ordinal = mref_ordinal;
    event->cta_x = blockIdx.x; event->cta_y = blockIdx.y; event->cta_z = blockIdx.z;
    event->warp_id = ((threadIdx.z * blockDim.y + threadIdx.y) * blockDim.x + threadIdx.x) >> 5;
    event->active_mask = active; event->predicate_mask = predicate_mask;
    event->executing_mask = executing; event->lane_id = lane;
    event->instruction_offset = instruction_offset; event->width_bytes = width_bytes;
    event->access_kind = access_kind; event->record_kind = ROUTE_B_LANE_EVENT;
    __threadfence_system();
}
