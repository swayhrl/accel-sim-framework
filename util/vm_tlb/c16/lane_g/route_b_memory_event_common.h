#pragma once
#include <stdint.h>

// Device records carry address lanes only: executing_mask = active & predicate.
// sequence is OBSERVED_CALLBACK_ORDER, never hardware-global time.
struct RouteBEventRecord {
    uint64_t observed_callback_sequence, launch_id, address;
    uint32_t static_index, mref_ordinal, cta_x, cta_y, cta_z, warp_id;
    uint32_t active_mask, predicate_mask, executing_mask, address_lane;
    uint32_t instruction_offset, width_bytes, access_kind;
};
struct RouteBBuffer {
    uint64_t next_sequence, overflow_count, drop_count;
    uint32_t capacity, reserved;
    RouteBEventRecord records[1];
};
