#pragma once
#include <stdint.h>
struct WRec { uint32_t static_index, active_mask, cta_x, cta_y, cta_z, warp; uint64_t addr[32]; };
struct WState { WRec* rec; unsigned long long count,overflow,seen; };
