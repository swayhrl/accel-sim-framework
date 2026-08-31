# Motivation telemetry source map

`EPL2MOTV1` is default-OFF (`-gpgpu_ep_l2_motivation_stats 0`) and is never
read by admission or scheduling control.

| Measurement | Production observation point | Source anchor |
|---|---|---|
| Frontend L2 demand-miss admission | Head of `m_icnt_L2_queue`, after L2 applicability and before preview; demand reads and writes included, `L1_WRBK_ACC`/`L2_WRBK_ACC` excluded | `src/gpgpu-sim/l2cache.cc`, `memory_sub_partition::cache_cycle` |
| 128-B normalization | `m_L2_config.block_addr(mf->get_addr())` | `l2cache.cc`, `ep_l2_motivation_record_reference` |
| Epoch reset | Existing kernel launch callback; primary stack/touch state is cleared there | `gpu-sim.cc`, `gpgpu_sim::launch`; `l2cache.cc`, `begin_ep_l2_b0_kernel` |
| Real eviction | Any valid victim from the side-effect-free preview, recorded only after the matching successful `l2_cache::access` commit; includes clean and dirty victims | `gpu-cache.cc`, `l2_cache::preview_access`; `l2cache.cc`, post-`access` event handling |
| WBUF allocation | Successful dirty-victim `WRITE_BACK_REQUEST_SENT`, after data-cache access/readout | `l2cache.cc`, `ep_l2_motivation_record_wb_create` |
| WBUF release | `L2interface::push()` immediately after it successfully enqueues an `L2_WRBK_ACC` into the per-slice `m_L2_dram_queue` | `l2cache.h`, `L2interface::push` |
| WAD lifetime boundary (not WBUF release) | `memory_sub_partition::set_done` calls `ep_l2_wad_complete` | `l2cache.cc`, `set_done` |

## Frozen primary classification order

The classifier uses the audited production preview order:

1. WAD same-address hazard / required-WAD-full (`WB_PATH`);
2. tag reservation/set replacement failure (`SET_ASSOC`);
3. line-MSHR, descriptor-pool, or per-address-cap failure (`MSHR_META`);
4. required MissQ entry shortage (`MISSQ_LOWER`);
5. timing-neutral dirty-victim WBUF shadow (`WB_PATH`) at C=4/8/16.
   `would_block` is an eligible frontend miss-admission **cycle/attempt** count,
   not a unique dirty-miss count;
6. any remaining failed exact admission predicate (`OTHER`).

This is exclusive classification of a frontend **demand miss** admission cycle
(read or write). For a write, MSHR and MissQ predicates participate only when
the production preview marks them required; locally absorbed writes do not
fabricate a resource demand. It is not a sum of independent existing M0a
counters. `OTHER` remains emitted
and is never renormalized away.
