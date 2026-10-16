# Ideal-mode source and lifecycle map

All source below is the Core candidate in BUILD_MANIFEST.json. Its Lane 1
parent is `126394be46b15f55b9756d43eb9ca9a9baae1c84`; the merge retains Lane 1's
production implementation. `CORE_MINIMAL.patch` is the delta from that parent,
not a request to merge every historical branch. Apply this patch after the
exact parent, then build once with all diagnostics OFF; Lane5 owns independent
qualification. Lane4 does not declare itself accepted. The diagnostic read
response uses the parent's actual requester admission/response audit hooks.

| Mode | Producer/consumer path | Preserved boundary |
|---|---|---|
| I_WB | gpu-sim.cc registration -> cache_config -> ep_l2_payload_store constructor -> const preview_free(WB) -> reserve() grows backing only at commit -> inherited ft_access copy phases -> lower_ready -> lower_accepted | Actual copy/read bank grants; WB packet sector versions; data release only after lower acceptance; independent WAD release at set_done |
| I_META | gpu-sim.cc -> mshr_table.m_ideal_meta -> full_reason / ensure_descriptor_available -> ordinary add / needs_lower_read / mark_ready / peek / commit | Capacities alone are non-binding; sector masks, pending atomic/order state and descriptor release after real response enqueue remain |
| I_READ_HIT | gpu-sim.cc -> memory_sub_partition frontend after ordinary ROP delay -> older producer/WAD/MSHR checks -> diagnostic role through same payload-bank arbiter -> ReferenceMemory snapshot -> real L2-to-ICNT FIFO -> pop retirement | No dropped request, synchronous callback, zero hit-delay shortcut, write/atomic bypass, or uninitialized cache-line data |

I_WB extra IDs retain modulo-4 banking. Appended slots are WB-only and
explicitly outside the nominal physical budget. WAD128 naturally bounds live
staging; no C-entry control ceiling is substituted. Diagnostic storage growth
does not grant another bank/port or remove copying.

I_META's dynamic vector updates descriptor accounting and keeps unsigned IDs;
it does not substitute a guessed large constant. Application capacity-full
counters must be zero before calling metadata non-binding. Histograms whose
historic bins stop at configured capacity must not be treated as proof of an
unbounded resource; use exact blockers, peaks and directed lifecycle evidence.

The read reference distinguishes known bytes and opaque cold/version symbols.
SASS performance runs do not prove numerical application output. Tests seed
real bytes, exercise masked stores and RAW/WAR response ordering, and verify
the same queued snapshots. Atomics remain on the ordinary producer path; this
pack does not claim a separate numerical atomic-opcode validation.

Default OFF preserves ordinary APIs. I_WB requires static FT mode 1; I_READ_HIT
cannot combine with WB/META or unified mode 2. Six CLI combinations reject
before workloads execute. The accepted I_WB_META combination is additionally
tested with 50 WB, 160 outstanding lines, 680 requesters and exact retirement.

Historical directed stress fixtures enlarge issue storage only to expose the
metadata allocator under test. The application overlays preserve primary
issue/DRAM/L1 settings. They are different evidence categories.
