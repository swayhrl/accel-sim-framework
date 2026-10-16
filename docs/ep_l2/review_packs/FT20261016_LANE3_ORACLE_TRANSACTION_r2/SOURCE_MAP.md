# Source / integration map

Core producer `5dd246028e3a3d997c1ad48aa85d8d77e98982ac`, engineering parent `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`.

- src/gpgpu-sim/ep-l2-ro-transactions.h: independent production candidate; lifecycle, sector masks, finite completion state, waiter-aware detach, same-address independent handles, callbacks for shared payload/pins/Tag visibility.
- src/gpgpu-sim/gpu-cache.h/.cc: mshr_table::reserve_ro_descriptor/release_ro_descriptor consume the original descriptor vector/free-list. reserve_ro_line/release_ro_line consume the original 128-entry map only in detach-with-MSHR mode. Full-reason accounting includes all native and RO requesters on the line. Old-static path with zero RO leases avoids a descriptor scan.
- tests/ep_l2/test_ro_transactions.cc: executes the actual module against shared production mshr_table and a small immutable byte/version reference port; this is not the final allocator adapter.
- util/ep_l2/ro_oracle.py: upstream SASS grammar from trace_parser.cc, full-epoch global read/store/atomic union, source/input/artifact hashes, SQLite and range output.
- util/ep_l2/run_ro_oracle_development.py: serial preprocessing of the five development workloads only; no simulator.

Historical rejected shortcut: write-allocate in gpu-cache.cc::wr_miss_wa_naive and wr_miss_wa_fetch_on_write creates read-shaped requests from stores. Current classifier requires certified line membership AND original GLOBAL_DEMAND_READ class, never !is_write() alone. Historical M3A audit is Framework 4f198e307361a2a5e4a38b4db478c5165f89752d:docs/ep_l2/review_packs/M3A_RO_CERTIFICATION_r1/.

## Required production adapter (Lane 1)

1. Verify oracle hashes and closed-world epoch/drain scope before enabling; stamp only original GLOBAL_ACC_R, not synthetic WA/atomic/writeback.
2. Invoke merge lookup before requesting a new landing; preview/reserve/commit must roll back an unused landing/Tag if shared descriptors refuse.
3. Bind payload_port live/pin/unpin, fill/response shared-bank service, Tag-generation validation/detach and handle-specific release to the sole common store. Never call reserve_resident's old address-sweep on detached RO objects.
4. Route every lower request and sector return by handle, not address; carry Tag binding independently; dispatch RO responses through L2-to-ICNT and commit only after enqueue.
5. Add separate default-OFF runtime config bits for detach and bypass; reject combinations with unverified oracle, static owner aliasing or unsupported epoch lifecycle.
6. Independent Lane-5 verification and qualified baseline/binary/config/run-key precede performance rows.

The published V1 interface is binding for identity; allocator pin/sector/owner transition methods and qualified baseline have not yet been published as executable consumers. This pack is a verifiable module/patch handoff, not an integrated full-cache implementation claim.

## r2 added input binding

Core src/gpgpu-sim/ep-l2-ro-oracle.h parses verified canonical range bytes and binds the manifest identity. It validates grammar/alignment/order; cryptographic verification belongs to the Framework preflight, not a claimed C++ hash implementation. Framework util/ep_l2/verify_ro_launch.py checks complete input/artifact hashes, exact producer identity and absence of inter-kernel host writes, and emits RO_INPUT_BINDING. No full-cache RO hooks or gpgpu runtime switch registration is claimed by this independent stage. The new shared payload API must expose actual RO roles, allocation/pins and Tag/return dispatch before Lane 1 integrates the module.
