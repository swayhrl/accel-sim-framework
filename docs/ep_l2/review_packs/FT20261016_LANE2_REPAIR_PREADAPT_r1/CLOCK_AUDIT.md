# Candidate physical vs native clock audit

| Producer / state | Candidate time source | Status |
|---|---|---|
| FT resident reads/writes, static copy source/destination, landing writes | physical gpu_sim_cycle + gpu_tot_sim_cycle from Lane5 clock delta | source check only for combined candidate |
| TVD frontend lookup/bank/ICNT response commit | existing actual cache_cycle physical now | retained; no memcpy offset |
| ordinary clean/dirty directory install, reclaim, rollback | ft_access physical_cycle | adapted this revision |
| promotion directory commit/age, WAD birth and WB retention birth | physical cycle read from GPU | adapted this revision |
| lower_ready/lower_accepted, set_done and epoch cleanup | existing production caller physical cycle | retained; new runtime validation pending |
| native data_cache access, Tag tvd_bind, host fill | original Tag timestamp with memcpy offset | native ordering preserved |

The actual sole bank request method retains Lane5's monotonic-physical-clock assertion. Source checks enumerate all four payload request sites in ft_access. Promotion must not pass its native Tag `time` to the directory/WAD lifetime state, which previously could become nonmonotonic against actual lower_accept/set_done. These additional TVD differences were not covered by the clock-only base test.

The production fixture now snapshots each bank's real grant counter around every cache_cycle + simpleDRAM cycle and asserts delta<=1, independently of the supplied Tag timestamp. Its host helper accumulates a real4096 memcpy offset and asserts no physical time or bank grant is consumed by untimed warming. New cases exercise actual warm-hit/clean retention/promotion and dirty forward/write/atomic/WAD/lower pressure. They are uncompiled/unrun until disk admission and official parent are available; old zero-offset12+3 results cannot qualify these boundaries.
