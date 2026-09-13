#include <stdint.h>

#include "retry570_targeted_memory_common.h"

extern "C" __device__ __noinline__ void capture_target_memory(
    int predicate, uint64_t address, uint64_t launch_id, uint32_t static_index,
    uint64_t record_address) {
    if (!predicate) return;
    unsigned int active = __ballot_sync(__activemask(), 1);
    unsigned int lane = threadIdx.x & 31;
    if (lane != static_cast<unsigned int>(__ffs(active) - 1)) return;
    TargetRecord* record = reinterpret_cast<TargetRecord*>(record_address);
    if (record->claimed == 0 && atomicCAS(&record->claimed, 0U, 1U) == 0U) {
        record->address = address;
        record->launch_id = launch_id;
        record->static_index = static_index;
        record->present = 1;
        __threadfence_system();
    }
}
