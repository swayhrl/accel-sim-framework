#include "common.h"
#include "utils/channel.hpp"

extern "C" __global__ void flush_channel(ChannelDev* channel_dev) {
  inst_trace_t terminal{};
  terminal.cta_id_x = -1;
  channel_dev->push(&terminal, sizeof(inst_trace_t));
  channel_dev->flush();
}
