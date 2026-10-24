#include "utils/channel.hpp"
#include "record_types.h"
extern "C" __global__ void ada_flush_channel(ChannelDev *channel) {inst_trace_t ma;ma.cta_id_x=-1;channel->push(&ma,sizeof(ma));channel->flush();}
