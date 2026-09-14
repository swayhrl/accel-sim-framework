#include <stdint.h>

#include "retry570_targeted_memory_common.h"

extern "C" __device__ __noinline__ void capture_target_memory(
    int predicate, uint64_t address, uint64_t launch_id, uint32_t static_index,
    uint64_t record_address) {
    TargetRecord* record = reinterpret_cast<TargetRecord*>(record_address);
    atomicAdd(&record->callback_count, 1ULL);
    if (!predicate) return;
    atomicAdd(&record->predicate_true_count, 1ULL);
    unsigned int active = __ballot_sync(__activemask(), predicate);
    unsigned int lane = threadIdx.x & 31;
    if ((active & (1U << lane)) == 0) return;
    atomicAdd(&record->active_lane_count, 1ULL);
    if (address == 0) {
        atomicAdd(&record->zero_mref_count, 1ULL);
        return;
    }
    atomicAdd(&record->nonzero_mref_count, 1ULL);
    if (lane != static_cast<unsigned int>(__ffs(active) - 1)) return;
    if (record->claimed == 0 && atomicCAS(&record->claimed, 0U, 1U) == 0U) {
        record->address = address;
        record->launch_id = launch_id;
        record->static_index = static_index;
        record->present = 1;
        __threadfence_system();
    }
}
