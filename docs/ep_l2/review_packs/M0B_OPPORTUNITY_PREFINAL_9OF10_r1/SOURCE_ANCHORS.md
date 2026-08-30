# Source anchors and frozen identity

| Item | Immutable identity |
|---|---|
| Promoted integration Core parent | `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e` |
| Promoted integration Framework runtime parent | `d61ffd23c926a25fa463a3e6e955c885b45f0f8a` |
| M0b Core producer | `9907b7e617ea0ee6580fb8156e985838720f08fa` |
| Frozen M0b Framework runtime candidate | `8a0299cab19a658d34b7a2dc0b6d91e8373c121b` |
| Post-freeze runner/parser/review helper SHA | `63084e5117640bc6fa4c729280517b25820e328d` |
| Branch | `hrl/ep-l2-m0b-opportunity-v0` |
| Core branch | `fork/hrl/ep-l2-m0b-opportunity-v0` |

The M0b producer is additive state guarded by default-OFF
`-gpgpu_ep_l2_m0b_stats`.  The sidecar map/counters are written only by the
source observation producers and read only for M0b reporting.  They are not
consulted by cache admission/replacement, payload allocation, MSHR transition
or retirement, WAD ownership/release, bank arbitration, lower routing,
scheduling, or DRAM behavior.

Relevant exact producer points:

| Observation | Native source event |
|---|---|
| new Line-MSHR instance | `l2_cache::access()` after accepted lower-read path (`gpu-cache.cc`) |
| actual lower issue | `memory_sub_partition::ep_l2_record_lower_issue()` at `L2interface::push()` (`l2cache.cc:1015-1023`) |
| first fill / readiness | `l2_cache::fill()` after native `baseline_cache::fill()` / `mark_ready()` |
| dirty victim / WAD | `l2_cache::access()` surrounding native WAD reservation and writeback creation |
| WAD release | native `memory_sub_partition::set_done()` (`l2cache.cc:2459-2463`) |

`mshr_table::commit_next_access()` retires a line but exposes no instance
completion callback; M0b does not infer completion from address reuse.
