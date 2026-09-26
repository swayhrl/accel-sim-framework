# Access-path source audit

Authority: Lane-B strong-reference source/binary at
`9efe8236e0c6338addfef5480e1da91bffb504eb`.

Evidence labels below are `VERIFIED_CODE` unless explicitly marked as a
diagnostic modeling decision.

## Current sequential ordering

1. `warp_inst_t::generate_mem_accesses()` receives per-lane addresses and
   creates coalesced `mem_access_t` transactions in `m_accessq`.
   `memory_coalescing_arch*()` preserves lane, byte, sector, operation, and
   transaction address state; atomic accesses use their separate coalescer.
2. `ldst_unit::memory_cycle()` sees the complete resident accessq. With
   `WARP_VPN_DEDUP_REFERENCE`, it scans from `entries.rbegin()`, which is the
   consuming `accessq_back()` side, forms exact legal page groups, and invokes
   the normal translation controller for one leader per unique VPN group.
3. `translation_controller::translate()` first honors existing inflight/READY
   and MSHR-waiter state. A new physical request must win the configured L1-TLB
   port. It enters `LOOKUP_L1_SERVICE` with `ready_cycle = cycle + L1 latency`.
4. `service_lookups()` waits for that interval, probes L1 TLB, and either marks
   the request READY on a hit or proceeds through L2, MSHR/PWQ, walker/PWC/PTE.
   An L2 or PTW request is never launched before the L1 result is known to miss.
5. Only a READY result calls `apply_ready_translation()` or the equivalent head
   `set_sim_pa()`. This preserves SimVA while attaching SimPA and source exactly
   once. A retry of the same UID finds inflight/READY/waiter state rather than
   launching duplicate physical work.
6. Only after `vm_translation_applied()` is true does
   `process_memory_access_queue_l1cache()` allocate a `mem_fetch`, derive the
   physical L1D bank, and enter the configured L1D latency queue. The frozen
   configuration has `-gpgpu_l1_latency 32`.
7. At the end of that queue, `m_L1D->access()` produces HIT, MISS,
   HIT_RESERVED, or RESERVATION_FAIL. A hit can complete the load/writeback;
   a miss/reserved request follows the normal cache/interconnect path. The L1D
   bypass path likewise requires translation before checking/pushing ICNT.

Thus the accepted model serializes the 10-cycle L1-TLB lookup before the
32-cycle L1D lookup. L1D hit/miss/reservation status is not known at the point
translation starts.

## Event dependencies

| event | waits for | does not imply |
|---|---|---|
| coalesced request resident | address generation/data coalescing | translation or cache admission |
| L1-TLB launch | request eligibility and finite TLB port | hit, READY, or data request |
| translation READY | all required L1/L2/MSHR/PTW work | address already applied |
| address apply | READY mapping/permission-compatible result | L1D bank admission or cache hit |
| L1D latency-queue admission | applied translation and free physical bank slot | cache hit |
| lower L2/ICNT request | applied translation and L1D miss/reservation outcome | eventual data completion |

## B1 source-composable overlap

The conservative VIPT-like diagnostic credits only overlap between the initial
10-cycle L1-TLB lookup and the 32-cycle L1D lookup:

`effective_L1_TLB_latency = max(10 - 32, 0) = 0`.

The existing L1D operation, physical tag/outcome, lower-level request, ports,
and all translation services remain unchanged. On a TLB miss this model hides
only the initial 10-cycle lookup, not the L2/PTW tail. Therefore the accepted
strong-reference 0/80 runs at commit `32854024...` are exact executions of this
minimum timing composition, although their original scientific role was an
L1-latency causal diagnostic.

This is `MODELING_DECISION`, not proof of RTX4080/Ada internals.

## Why B2 is not integrated

The current L1D path allocates and indexes a `mem_fetch` only after SimPA is
attached; cache tags and lower requests are physical. It has no integrated
virtual L1 tag/permission state, ASID-aware synonym handling, reverse mapping,
virtual-cache coherence, or shootdown protocol.

Serving a nominal L1 hit without translation would therefore either assume the
answer from the future or silently change correctness semantics. B2 is retained
only as a logical bound fixture and is `NOT_IMPLEMENTED`, as explicitly allowed
by the Goal.

## Source receipts

- `src/abstract_hardware_model.cc` SHA-256
  `162f04692af8e3aaa4f42d9df83c40f56b9af98d13d4e8bc442ca37706a3a51a`;
- `src/gpgpu-sim/shader.cc` SHA-256
  `482fd8924a4c844dc38319700b0055000f9921fc6b1f9bed703e97c68efa08b6`;
- `src/gpgpu-sim/vm_translation.cc` SHA-256
  `6acb6149811cd48849ca299c56584e5ecf9e0551d71265b483f520631e2abead`;
- `src/gpgpu-sim/gpu-cache.cc` SHA-256
  `8b8fcc3f9356da6005d0898c50298553270484ba58bcab1765ef5615e75d7cbb`;
- frozen binary SHA-256
  `ff43ee33257fac6171ddb31a81a561e10691b5c52d2127545719f6ba8709bef0`;
- config SHA-256
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`.
