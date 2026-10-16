# Source/consumer map

- `src/gpgpu-sim/ep-l2-ft-interface.h`: exact Lane 1 public PayloadHandle ABI from Core 4fb91f0a; cherry-picked with provenance, not independently defined.
- `src/gpgpu-sim/ep-l2-tvd-directory.h`: fixed-capacity shared-directory state, non-mutating preview, revision-checked commit, sector-exact lookup, read references, same-handle promotion, WB phase boundaries and epoch drain.
- `tests/ep_l2/test_tvd_directory.cc`: clean/dirty tests invoke the actual directory and historical production `ep_l2_payload_store::request` bank arbiter. Version backing exists only in the test and is keyed by the returned canonical payload ID.
- `tests/ep_l2/run_tvd_directory.sh`: isolated one-process compiler/runner; optional ASan+UBSan.

Pending producer wiring by the public integration owner:
1. `l2_cache::access`: real selected clean victim, resource preview/reserve/rollback, new landing and old retained handle.
2. Tag-miss pipeline before generic WAD denial: extra cycle, directory preview, sectors, dirty read-forward, shared descriptor/response ownership.
3. Actual bank request and L2-to-ICNT push: allocator pin/unpin and read lease commit.
4. `L2interface::push`: after actual lower acceptance, bind packet to directory ticket; lower-data ownership must be explicit.
5. `memory_sub_partition::set_done`: WB completion; release WAD obligation or retain clean metadata.
6. Actual tag assignment/invalidate/flush: same-handle promotion and epoch drain.

No existing `gpu-cache.cc`/`l2cache.cc` production call site is patched yet. Therefore these module fixtures do not establish end-to-end L2-cache TVD service.

Full-directory promotion additionally uses preview_dirty_promotion/commit_dirty_promotion in the same module, with a real canonical handle for the displaced dirty resident. This remains a metadata producer boundary test, not an l2_cache call-site test.
