# Dynamic GROUP_FULL_M patch semantic isolation

The patch is based on AutoAWQ `c7b0e88c327694c715b0a758d9ce8fd414a1fa21` / generator blob `98f49efac8626388039912e6aabc8a84d9f8303b` and creates a new independent extension without replacing accepted binaries.

The target m16n128 kernel computes dynamic `m_tiles=ceil(M/16)`, ROW and GROUP coordinates, and the branch-free integer selection `row + mapping_mode*(grouped-row)`. Every scientific cell passes mapping_mode=1, so M1/16/32/64 and split1/8 use the same compiled target kernel and the same GROUP_FULL_M instruction path. There is no M-dependent branch in the GEMM body.

All A/input, qweight/qzeros/scales, and C/output pointer formulas downstream of reconstructed `blockIdx_y` are unchanged. Exhaustive enumeration proves exact output coverage and equality with the ROW-reference address unions for every M/split. K-loop/interleave, loads, barriers, shared layout, dequant, MMA, writeback, tile, block, tensor layouts, split, scratch, and reduction are unchanged.

Host-only checks freeze M={1,16,32,64}, K=4096, N=12288, group=128, split={1,8}, and mapping_mode=1. Split1 keeps the accepted direct-plane return; split8 keeps `sum(0)`. The m16n64 kernel and `pybind_awq.cpp` remain unchanged.
