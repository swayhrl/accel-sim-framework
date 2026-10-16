# Lane 2 -> Lane 1 / Lane 5

Exact consumed interface: Framework cb7d92e4edde97e81520cfdd00762dfe81ee9b20 / Core 4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617. Current candidate Core: `56abbacc1192d68995e78561899719649f838079`.

1. Start with public identity ABI 4fb91f0a. Apply CORE_MODULE.patch from FT20261016_LANE2_DIRTY_MODULE_r2 (supersedes clean module patch); it adds only directory/test/runner. Do not cherry-pick both versions as independent additions.
2. Instantiate the directory as the shared WAD/TVD authority, replacing/extending the existing WAD address set. No second address CAM/allocator. Both features default OFF.
3. Executable dependencies: real reserve/rollback/role-transfer/pin, actual victim-selection callback, true one-cycle tag-miss lookup/response path, atomic same-handle promotion, lower-accept with accounted independent data, set_done and epoch drain. V1 currently describes these but publishes only identity ABI.
4. A full directory can promote clean A while displacing dirty resident B using preview_dirty_promotion/commit_dirty_promotion to reuse A's address slot atomically; no 129th slot. Prepare actual lower/control resources before this metadata commit.
5. Dirty forwarding must precede generic WAD-read denial; missing sector reads and all writes/atomics to mandatory WB wait correctly. Never replace this with unconditional wait-until-WB behavior.
6. After wiring exact source, run every NOT_RUN gate in PRODUCTION_GATES.csv with actual memory_sub_partition producers and a data/version reference. Lane 5 must not launch TVD performance rows from this module-only receipt.

No formal simulations launched. Test-only data backing is not an additional production data array or performance proof.
