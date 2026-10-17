# r19 WB residency observer interpretation

No correctness failure or runtime change: existing source/qualification/results remain. FT wb_occupancy_sum samples occupied WB-role slots **after lower drain**; dynamic roles include unified borrowed slots, so this is not a dedicated-only counter. FT staged_max is an event peak of m_ft_wb records, a different object/phase. Zero sampled occupancy does not establish zero transient WB or residence.

FT staging_lifetime starts at baseline copy readout versus unified producer commit, ends at lowerFIFO acceptance, and excludes later DRAM set_done/WAD retention. Cross-mode averages do not share identical start bounds. Compare same-mode across conditions, retain raw values, and use separately defined WAD lifetime, real issue/credit/return pressure and terminal drain. No continuous integral, common p95, GPU stall attribution or C1 headroom is fabricated. Exact pinned source excerpts/hashes attached. H0 five accepted pairs/0.16% unchanged.
