#pragma once
#include <stdint.h>

// P4 transport payload.  Sequence remains transport-only and is not part of
// final C16WARP1 serialization.
struct c16_p4_wrec_t {
    uint32_t static_index, active_mask, cta_x, cta_y, cta_z, warp;
    uint64_t addr[32];
};
struct c16_p4_packet_t {
    uint64_t sequence;
    c16_p4_wrec_t record;
};
static_assert(sizeof(c16_p4_wrec_t) == 280, "C16 WRec contract");
static_assert(sizeof(c16_p4_packet_t) == 288, "P4 transport contract");
