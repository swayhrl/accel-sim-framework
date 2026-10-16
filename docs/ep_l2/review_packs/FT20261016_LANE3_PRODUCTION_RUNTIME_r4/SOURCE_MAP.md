# Exact consumption and implementation map

- Scientific contract: Framework 6c136e2a56a008695f8c8b815723bf8f1a760db9.
- Current continuation: Framework aec01450d3c527524ee09ee59242f582fafe5354, review_r2 only.
- Lane 1 frozen R0 Core parent: 126394be46b15f55b9756d43eb9ca9a9baae1c84, merged on Lane 3 with its current production interfaces. R0 binary was never rebuilt/modified.
- Lane 3 prior shared-store module: ddedbf0fabd46c6e35358c9a0e78b77f52cab2c5; retained and adapted, not confused with old independently checked 57801b42.
- Lane 3 new frozen Core: ac3028b00aa37c08b2210b1c9a1fe8444060c0f9.
- Frozen Framework runtime source: c3f8f11ed4a5bf722307154a66193fbbce1715d8.
- Framework driver patch exact parent: 37dec04d223ae65167c5584e56887c74f6540d27. Existing driver before r4 is byte-equal to this parent's driver; only the shown RO hooks are added.
- Oracle input producer: d2ba33bd92c68f176294c9b5d5a22d3d7b7f8489; input verifier: 28a594c78bc7568ca038f63ef8122ff7337b7d2c. Five immutable records remain in FT20261016_LANE3_ORACLE_TRANSACTION_r2/inputs and are indexed by its INPUT_INDEX.json.

`src/gpgpu-sim/ep-l2-ro-runtime.inc` implements actual Tag callbacks and routes RO via l2_cache. Attached lookup reads the actual Tag's payload handle; only detach-with-native-MSHR mode consults `mshr_table::lookup_ro_line`. Bypass mode never discovers a detached transaction by line address. Bounded completion scanning selects ready responses; it is not an address-merge lookup.

`ep-l2-ft-cache.inc` reuses actual R0 allocation/dirty-victim/WB/WAD machinery, then diverts eligible RO misses before native descriptor allocation. Clean, unpinned resident sectors may be adopted; foreign native response pins, dirty resident data and pending native fills stay on the ordinary path. Detached reuse starts with a real Tag miss and a fresh payload handle. No address-wide completion cleanup occurs.

`gpu-sim.cc` registers two OFF defaults, activates once at the first launch after initialization/drain, rejects in-epoch host writes, and exposes explicit end-after-drain. `gpu-simulator/accel-sim.cc` binds the actual commandlist before parsing, rejects copies after the first kernel command even within a parse window, and closes the single whole-commandlist epoch after hardware drain. It never shrinks the epoch per kernel.

`l2cache.cc` routes marked RO lower packets from actual ReturnQ through common RAM bank writes. Denied packets remain in that queue. The existing L2→ICNT enqueue calls commit in the granted read cycle; descriptor/payload leases survive backpressure. Lower packets retain payload id/generation and their sector mask. Existing packet version storage is reused; no extra persistent response-data copy exists.

`prepare_ro_runtime.py` checks the small frozen binding/manifest/range chain and emits only the RO overlay plus a config receipt. It preserves existing trace-content identity and does not rehash full traces. It is a configuration tool, not launch qualification: the Lane 5 runner still verifies complete trace contents and complete ordered config/source/binary identity before execution. Core independently checks manifest/range bytes and actual commandlist hash. This is an explicit TRACE_MODEL_CLOSED_WORLD oracle, not proof of unobserved CPU/DMA/alias behavior.
