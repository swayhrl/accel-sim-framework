# Lane 2 actual clean TVD production — r1

Status: **CLEAN_PRODUCER_READY_FOR_INDEPENDENT_VALIDATION**. Full/dirty production TVD is not qualified by this checkpoint. Consumes exact R0 Core 126394be46b15f55b9756d43eb9ca9a9baae1c84 and preserves its frozen binary. The four new scenario groups execute memory_sub_partition/cache_cycle, real selected victims, L2interface/memport, actual ICNT push and set_done. Prior seven directory fixtures are not rerun.

Verified: clean selected victim keeps its canonical payload in the sole R0 allocator; Tag-miss serialized one-cycle lookup; actual same-bank refusal and full one-entry ICNT queue; successful response commit and no read promotion; partial-sector fallback; same-handle write promotion with dirty resident WB; flush/invalidate reclaim. Shared WAD/TVD uses 128 total addresses; legacy WAD address set is not populated in TVD mode. New flags default OFF and require unified FT mode with WAD128.

Symbolic version reference compares clean A=0 against a dirty current resident B with a different nonzero request-UID version, and checks promoted A's later write version. This is model-level sector-version/request identity evidence, not full-byte/atomic numerical evidence.

Matched OFF/ON within the same directed binary: actual lower read packets 2 -> 1, actual accepted lower read bytes 64 -> 32. `served_sector_bytes=32` labels response service, never automatically DRAM savings. This small explicitly scripted sequence is not a performance application result. All scientific application rows remain NOT_RUN under Lane 5 ownership.

CORE_MINIMAL.patch applies to exact R0. Lane 1 remains final public integrator; Lane 5 independently qualifies this delta without delaying R0 B16/U_WB. Dirty production tests continue after this clean-first frozen checkpoint.

Patch uses zero context to avoid whitespace-only context in the evidence file. Apply with `git apply --unidiff-zero CORE_MINIMAL.patch` on exact R0, then build.
