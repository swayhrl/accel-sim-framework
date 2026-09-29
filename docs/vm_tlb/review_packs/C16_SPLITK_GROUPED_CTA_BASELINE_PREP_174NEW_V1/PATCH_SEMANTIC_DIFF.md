# Grouped CTA patch semantic isolation

The new independent extension is based on AutoAWQ `c7b0e88c327694c715b0a758d9ce8fd414a1fa21` / generator blob `98f49efac8626388039912e6aabc8a84d9f8303b` and does not replace accepted binaries.

The target m16n128 kernel receives runtime `mapping_mode`. It computes ROW and GROUP_M16 coordinates unconditionally, selects with `row + mapping_mode*(grouped-row)`, reconstructs logical `blockIdx_y=Mtile*384+Ntile`, and keeps `split_z=blockIdx.x/6144`. There is no mapping-dependent kernel branch; both modes use the same compiled kernel and added integer path.

All downstream A/input, qweight/qzeros/scales, and C/output pointer formulas are unchanged and consume only reconstructed `blockIdx_y`. Exhaustive enumeration proves that each logical output tile is covered once in both modes, so each tile reads the same A rows and weight-side N tile and writes the same output range. Only traversal order differs.

K bound/interleave, global load counts, barriers, shared layout, dequantization, MMA, writeback, tile, grid, block, scratch, split, and reduction are unchanged. The host wrapper only freezes M/K/N/group/split/mode and retains accepted split1 direct output versus split8 reduction. Data tensors retain their original 2D layouts. The m16n64 kernel and `pybind_awq.cpp` are unchanged.
