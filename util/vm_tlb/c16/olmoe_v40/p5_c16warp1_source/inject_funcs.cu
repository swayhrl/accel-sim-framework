#include <stdint.h>
#include "utils/utils.h"
#include "utils/channel.hpp"
#include "p4_c16_packet.h"

// P4 preserves the official helper ABI: pred, static identity, MREF address,
// launch value, ChannelDev pointer.  No global progress wait is introduced.
extern "C" __device__ __noinline__ void instrument_mem(int pred, int static_index,
                                                       int selected_static, uint64_t addr,
                                                       uint64_t sequence_base,
                                                       uint64_t pchannel_dev,
                                                       uint64_t sequence_counter_ptr) {
    if ((uint32_t)static_index != (uint32_t)selected_static) return;
    if (!pred) return;
    const unsigned mask = __ballot_sync(__activemask(), 1);
    const unsigned lane = get_laneid();
    c16_p4_packet_t packet{};
    for (int i = 0; i < 32; ++i) packet.record.addr[i] = __shfl_sync(mask, addr, i);
    packet.record.static_index = static_index;
    packet.record.active_mask = mask;
    int4 cta = get_ctaid();
    packet.record.cta_x = cta.x;
    packet.record.cta_y = cta.y;
    packet.record.cta_z = cta.z;
    packet.record.warp = get_warpid();
    // P5 integrity token.  There is deliberately no sequence-order wait.
    if (lane == (unsigned)(__ffs(mask) - 1)) {
        packet.sequence = atomicAdd((unsigned long long*)sequence_counter_ptr, 1ULL);
        ((ChannelDev*)pchannel_dev)->push(&packet, sizeof(packet));
    }
}
