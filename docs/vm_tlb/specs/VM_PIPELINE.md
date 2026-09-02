# VM pipeline (M1)

`TraceAddr -> SimVA -> coalescing -> mem_access_t VM hook -> SimPA -> L1D or
bypass path -> L2/DRAM`.

`warp_inst_t` creates coalesced `mem_access_t` records. The hook is at
`ldst_unit::memory_cycle()` before the first `mem_fetch` allocation and before
the real L1D/data path. It is therefore transaction-granular, not lane-granular.

At 64KB, existing coalesced transactions are asserted not to cross a page; the
M1 helper test exercises both the non-crossing and crossing predicates. A future
backend may replace ideal identity mapping with TLB/PTW service, but must retain
both addresses and block real data access until translation completes.
