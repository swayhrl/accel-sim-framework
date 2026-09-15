#pragma once
#include <stdint.h>
struct C16Rec { uint32_t static_index; uint32_t active_mask; uint64_t addr[32]; };
struct C16Ctr { unsigned long long count; unsigned long long overflow; };
