# r17 first three accepted pairs: pressure and downstream observations

All observations below are from the exact currently accepted repaired release, same five predeclared cohort; no new trace/config/test/experiment or partial group average. Raw/CSV identities and current V2 binding are recorded. Events/bytes are source-defined sums across64 slices; per-slice peak maxima and slot-cycle means are labeled explicitly, not whole-GPU elapsed cycles. Legacy C1 resident-headroom is not used.

SAD is the predeclared near-tie negative control. B/U cycles110773/110749, peak1/1, WB-data-full0/0, pool-full0/0, same3975 completed WB and508800 DRAM write bytes. Bcopy3975→U0 and bank ops483611→475661; no above-C16 staging observed. It demonstrates removed copy operations, not capacity benefit or statistical significance.

vectorAdd_4M is a non-negative-control workload with observed pressure: B staged peak16 and440161 WBUF-full events; U peak35 with0 WBUF-full and0 pool-full. Copy100568→0; logical bank ops2801704→2600516; bank waits445678→367415. Yet native cycles73696→73549 (1.0019986675549633x) remain near tie. L2-to-DRAM-full source events increase1103500→1763609, scheduler-full975968→974186. Read bytes stay32000000; write bytes12872704→12866048, completed WB100568→100516. The run observes the unified staging role exceeding16; it does not isolate a capacity-caused speedup from copy removal, mapping or changed scheduling.

CFD cycles79093→79262 (0.9978678307385632x), preserving regression. Copy31123→0; bank waits102546→91029; peaks16/16; baseline WBUF-full only5. WAD hazards9841→13400 and DRAM scheduler-full101780→102720 increase. DRAM read bytes6793856→6790784 and write bytes3983744→3976064 vary slightly with scheduling/coalescing; WB31123→31063. Lower bank/copy counts therefore do not by themselves predict elapsed-cycle gain.

The evidence motivates pressure/downstream localization after the fixed five pairs, without expanding traces, dropping negative results, asserting unmeasured cause, or executing new static partitions/Ideal/TVD/RO. Those still need their own scientific contract/config/source/binary qualification. All5 accepted pairs are required before geomean.
