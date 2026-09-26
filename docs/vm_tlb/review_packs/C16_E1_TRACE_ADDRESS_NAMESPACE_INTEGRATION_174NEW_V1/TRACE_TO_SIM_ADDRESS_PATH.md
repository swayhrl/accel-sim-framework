# Trace to simulator L2 address path

| Hop | Source/function | Address behavior |
|---|---|---|
| traceg serialization | qualified `.traceg.xz` instruction record | NVBit MREF numeric addresses serialized as hexadecimal lane addresses. |
| parser | `gpu-simulator/trace-parser/trace_parser.cc:136-225`, `inst_trace_t::parse_from_string` | List mode reads each address directly; base/stride and base/delta only reconstruct the encoded lane values. No mask, address-space translation or partition mapping is applied. |
| instruction operand | `gpu-simulator/trace-driven/trace_driven.cc:247-255` | `set_addr(i, trace.memadd_info->addrs[i])` copies the numeric lane address exactly. |
| local/global distinction | `trace_driven.cc:634-662` | Only local-space operands enter `translate_local_memaddr`; global operands are unchanged before `generate_mem_accesses`. |
| coalesced transaction | `src/abstract_hardware_model.cc:294-763` | Baseline coalescing forms deterministic 32/64/128-byte transaction addresses. This is alignment/transactionization inside the same numeric namespace, not a VA remap. |
| `mem_access_t` | `src/abstract_hardware_model.h:845-882` | Constructor initializes `m_addr`, `m_sim_va` and `m_sim_pa` from the coalesced address. Canary uses VM mode 0, whose bypass leaves `m_addr` unchanged. |
| `mem_fetch` | `src/gpgpu-sim/mem_fetch.cc:41-70`, `mem_fetch.h:90` | Copies `mem_access_t`; `get_addr()` returns `m_access.get_addr()`. DRAM partition address is calculated separately and does not replace `m_addr`. |
| sector children | `src/gpgpu-sim/l2cache.cc:740-805` | A 128-byte request may form 32-byte children at `parent_addr + 32*i`; this is deterministic sector splitting in the same namespace. |
| L2 input | `src/gpgpu-sim/gpu-cache.cc:2350-2359` | `l2_cache::access` receives and logs `mf->get_addr()` unchanged. |
| set/partition index | `gpu-cache.cc:202-211` | `partition_address(addr)` is used only to compute the cache set index; it never mutates `mem_fetch::get_addr()`. Same set is not used as namespace evidence. |
| oracle lookup | `gpu-cache.cc:107-120` | Eligibility is non-write `GLOBAL_ACC_R`; lookup consumes the exact `mf->get_addr()` numeric value. |
| PTE/synthetic path | `src/gpgpu-sim/gpu-sim.cc` physical `PTE_ACC_R` construction | PTE traffic is already physical, uses a distinct access type and is rejected before oracle target admission. |

For the selected L0/L14/L27 canaries, every observed hop is exact numeric equality. Across arbitrary lane accesses, only deterministic baseline coalescing/sector alignment may change the individual lane value; the 28 target intervals are 128-byte aligned, so transaction formation cannot cross into or out of a target interval for an in-range target access.
