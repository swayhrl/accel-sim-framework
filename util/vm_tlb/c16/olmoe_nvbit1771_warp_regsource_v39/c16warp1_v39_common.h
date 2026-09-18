#pragma once

#include <stdint.h>

// Exact historical C16WARP1 payload.  This structure is deliberately kept
// separate from the Channel envelope; it is the scientific/on-disk contract.
struct c16warp1_wrec_t {
    uint32_t static_index, active_mask, cta_x, cta_y, cta_z, warp;
    uint64_t addr[32];
};

// Transport-only envelope.  Sequence is not written into C16WARP1.
struct c16warp1_packet_t {
    uint64_t sequence;
    c16warp1_wrec_t record;
};

struct c16warp1_device_counters_t {
    unsigned long long producer_records;
    unsigned long long producer_overflow;
    unsigned long long producer_next_to_push;
};

static_assert(sizeof(c16warp1_wrec_t) == 280, "C16WARP1 WRec size changed");
static_assert(sizeof(c16warp1_packet_t) == 288, "Channel packet layout changed");
