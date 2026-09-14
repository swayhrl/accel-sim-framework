#pragma once
#include <stdint.h>

// C16_ROUTE_B_LANE_EVENT_V1.  A record is one executing lane, never an
// implicitly reconstructed warp address-array.  Every lane record carries an
// explicit warp_instruction_instance_id allocated once by the executing-warp
// leader then broadcast to its peers.  observed_callback_sequence is only
// OBSERVED_CALLBACK_ORDER, never hardware-global time.
enum RouteBRecordKind : uint32_t { ROUTE_B_LANE_EVENT = 1, ROUTE_B_TERMINAL = 2 };
struct RouteBLaneEvent {
    uint64_t observed_callback_sequence, warp_instruction_instance_id;
    uint64_t launch_id, gpu_va;
    uint32_t static_index, mref_ordinal, cta_x, cta_y, cta_z, warp_id;
    uint32_t active_mask, predicate_mask, executing_mask, lane_id;
    uint32_t instruction_offset, width_bytes, access_kind, record_kind;
};
struct RouteBBuffer {
    uint64_t next_sequence, next_warp_instruction_instance;
    uint64_t overflow_count, drop_count;
    uint32_t capacity, terminal_status;
    RouteBLaneEvent records[1];
};
