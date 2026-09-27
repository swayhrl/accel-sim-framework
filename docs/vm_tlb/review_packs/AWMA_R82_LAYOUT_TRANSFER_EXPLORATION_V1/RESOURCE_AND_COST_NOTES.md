# Finite resource and cost notes

- P1 B0/C1 stage1: 8 warps, 58 registers/thread, 1024 B dynamic shared, no global scratch.
- P1 B0/C1 stage2: 4 warps, 26 registers/thread, 1024 B dynamic shared, no global scratch.
- FLA selected audit artifact: 4 warps, 228 registers/thread, 10240 B dynamic shared, no global scratch.
- `cuobjdump` reports static `SHARED:0` because Triton supplies these allocations dynamically; the Triton metadata JSON is the shared-byte authority.
- C1 changes no register or shared allocation. It removes three stage2 shared stores in the final cubin but retains the conversion and all five barriers; the paired timing has no reproducible benefit.
- No PPA, occupancy extrapolation, data-cache/TLB inference, or barrier-stall time summation is made.
