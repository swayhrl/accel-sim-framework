# Resource vector and residence accounting

**Scientific disposition update,2026-10-16:** under
[authorization5248a5ed](DERIVED_INPUT_AUTHORIZATION_V1.md), the original Btree,
2DConvolution and LUD results retain terminal/invariant PASS but are
`FORMAT_APPLICABILITY_REVIEW_PENDING`. This applies to the Btree/2D matched128
numbers described below as well as primary, control and reused-baseline rows.
Their mechanical pair validation does not close scientific applicability.
Original Hotspot remains HOLD; the new V2 results use a separate admitted
source-profile lineage and never replace its original identities.

This materializes the method registered in R2 before comparative outcomes. [RESOURCE_VECTOR.tsv](review_pack/resource_vector_v1/RESOURCE_VECTOR.tsv) derives seven arms from registered config inheritance and original canonical baseline startup echoes. [RESOURCE_SOURCE_HASHES.tsv](review_pack/resource_vector_v1/RESOURCE_SOURCE_HASHES.tsv) binds those sources. No parameter, input, workload membership or performance-selection criterion changes.

All counts are per SM except the explicitly global lower-credit cap. Enabled data capacities are16KiB B16-N/WAIT128,80KiB TC80-N,96KiB enhancedTRAD96, and80KiB DTC plus its existing16KiB ordinary side path. DTC's16KiB logical search coverage adds128 mappings, not another16KiB of data. The ordinary side path is sector-based in the DTC configuration; structural traditional controls are whole-line128B. Extra Tag/PIB/Ref/waiter/transaction state and independent data services remain charged separately. The historical platform's configured96KiB shared capacity stays present in each arm; it is not silently counted as additional DTC data or removed to create a favorable comparison.

The enhanced traditional arm has768 enabled searchable lines, PIB256 and512 effective MSHRs with merge8. B16-N/TC80-N/WAIT128 have32 effective MSHRs with merge8: their literal parsed512 is overridden only in PAPER_BASE. IO/OO retain the ordinary side path's512 MSHRs, alongside their own candidate/miss ownership. IO uses256 PIB records, OO128, and the matched IO control128. Their physical pool is640 lines; its pending lower requests cannot be counted again as another640 data lines. Candidate queues are bounded by PIB depth and physical ownership bounds the aggregate retained/pending lines. The32768 credit cap is global and is not32768 per-SM transaction entries.

The ordinary cache has its existing32B data and fill services. Finite DTC separately declares32B/core-cycle refill,128B/core-cycle collection, four waiter updates/core-cycle in OO and one successful retirement/core-cycle using the common operand collector. Tag latency is one core cycle with four registered banks; the delivered reference initiation on the qualified LD/ST multiplier1 path is narrower than the aggregate four-bank ceiling. Last-reference/release metadata updates use the registered32-lane assumption. Ready selection scales with PIB depth; slot generations, per-instruction reference vectors, waiter identity, ready/pending state and the priority/ordering logic remain real cost, not free storage.

OO's explicitly configured13-bit Ref field totals640×13=8320 raw bits per SM. This is **one field**, not an estimate of complete metadata area. Mapping pointers, addresses, replacement state, generations, sectors, PIB operands, merge records and ports require implementation-specific costing; host C++ object sizes are not that estimate. IO's reclamation bookkeeping is different and is not assigned an OO Ref array it does not implement.

`ordinary_host_max_geometry_bytes` is exposed separately: with adaptive sizing OFF, the legacy unified-size option may still reserve a larger host metadata backing structure than the enabled associativity searches. This is a simulator allocation bound, not proof of a corresponding fabricated data SRAM. Conversely, on the adaptive modern platform the per-kernel enabled L1/shared allocation is essential. Do not use these host vectors as proof of common physical storage, equal total area or a passing modern128KiB capacity gate. The [modern audit](MODERN_CAPACITY_CONTRACT_REVIEW.md) remains HOLD.

`snapshot_service_closure.py` emits `RESIDENCE_AND_OCCUPANCY.tsv` only for strict terminal finite rows. PIB and physical occupancy are cycle integrals divided by64×whole-workload core cycles, including idle SMs and gated/terminal intervals. These are all-SM averages, not active-SM-only averages. Physical occupancy includes retained mapped data after instruction references finish. The fully-admitted-and-ready timestamp is separate from retirement; sums divide by retired cacheable warp instructions (one PIB instruction), not active-thread instructions. The complete-workload instruction counter is separately the active-thread count; both original counters and denominators remain unchanged. Ready-to-collection, collection duration and post-collection writeback wait retain separate columns and their sum must reproduce ready-to-complete. Map-loss-to-free divides by mapping-loss release events, including immediate releases; zero events are NA, not invented zero latency.

Primary IO256 versusOO128 does not isolate ordering from waiting depth. The fixed matched IO128 controls require complete valid scopes before a matched-depth causal interpretation. No incomplete cohort average or native DTC/equal-area conclusion is produced. The completed CPU body audit of all629 members confirms≤32 global128B references and no cacheable local-load form for these inputs. It also discovers a [Hotspot shared-format boundary](HOTSPOT_SHARED_FORMAT_REVIEW_V1.md); affected comparison promotion and three unlaunched rows are HOLD. This does not qualify new ISA domains or justify changing the frozen input silently.


`collect_service_closure_matched.py` now emits an explicit four-pilot `MATCHED128_GATES.tsv`, pair audit and terminal-only `MATCHED128_METRICS.tsv`. It binds the unchanged plan/spec hashes and complete ordered input/member/instruction scopes; checks common Core/build Framework/binary, finite enable, physical640/logical128 organization, and effective inherited options from immutable attempt snapshots. It requires IO/OO active depth128 in both declared configuration and actual startup echoes. The complete config lexer supports the original multiline quoted DRAM timing value. No simulator parser/configuration was modified.

The literal allowed differences are recorded, not hidden: mode2 versus3, and IO depth128 versus the OO configuration's inactive IO-only setting256. Core6fba0136 `shader.cc` constructs the IO frontend only for PAPER_IO and the OO frontend only for PAPER_OO; their separate admission/lower-candidate paths use their respective depths. Other options must match. This is equal active waiting depth; it is not equal total metadata or area. Both terminal rows must separately pass the full strict collector, with identical retired cacheable warp instructions and collected32B sectors. Pending pairs receive no metrics; Hotspot stays admission HOLD.

The first complete pair is Btree,444467849 total active-thread instructions,1817551 retired cacheable warp instructions and4139841 collected32B sectors in each arm. IO128/OO128 cycles are247940/173210. Their ready-to-complete means are167.6345/10.2981 core cycles per cacheable warp instruction; map-loss-to-free means316.3103/0.9616 cycles per release event. Occupancy remains the all64-SM cycle average, not an active-only average. The export also retains separate ready-to-collect, collection and writeback waits, raw sums/integrals and exact UUIDs. This is one fixed-model mechanism observation; the remaining fixed pilots and full cohort retain their existing identities and gates.

The second complete pair is2DConvolution,620347492 active-thread instructions,4716288 retired cacheable warp instructions and21984780 collected32B sectors in each arm. IO128/OO128 cycles are694704/592346. Fully admitted ready-to-complete means are388.7317/8.2900 core cycles per cacheable warp instruction; the separate collection and writeback means remain explicit. Mean PIB occupancy is126.194881/126.205080 entries per SM, so OO does not reduce that metric here. Physical occupancy is218.531091/188.860210 lines per SM. Map-loss-to-free events differ3843941/3290844; their means1077.840803/735.456553 use each arm's own event denominator. Exact gates, raw sums/integrals, identities and both full strict receipts are retained in [matched128_v2](review_pack/matched128_v2). BICG subsequently completed its full matched128 gate and residence checks: IO12893312525/OO12847533116cycles,2097152 cacheable warp retirements and19922944 collected32B sectors each; see checkpoint_20261016T1620Z and final checkpoint_20261016T2133Z. Hotspot remains held. Neither the active-depth match nor these two workload observations establishes equal total metadata/area or a general native-hardware conclusion.

Twenty-four CPU validation guard checks cover all four registered contracts and reject primaryIO256 as matched128, changed binary, changed input scope, finite OFF and changed physical capacity. They are validator tests, not extra simulated/native diagnostic conditions. Their receipt and the collector SHA are retained in the dedicated matched128 review pack. No simulation was repeated for these checks.

`LOWER_RESOURCE_PRESSURE.tsv` exposes strict terminal finite rows' actual global lower-cap echo, reported cap-full events, mode-specific candidate-queue-full stalls, acquired/released credits and final outstanding count with stdout SHA. It preserves missing fields as unavailable, never zero. This is not a measured peak, proof that every pipeline is unconstrained, or an ordinary-baseline pressure qualification. Positive events would be retained without retuning the registered32768 cap. Hotspot rows keep their promotion HOLD.

The initial CPU-only [interconnect identity audit](review_pack/interconnect_identity_v1/ROW_INTERCONNECT_IDENTITIES.tsv) verifies all44 registered inherited configurations selectnetwork_mode2 (LOCAL_XBAR), with33 actual startup observations at that checkpoint. Core6582b9d1/6fba0136 `icnt_wrapper_init` constructs that path from inline options; only mode1 opens the external interconnect filename. Thus the inactive default`mesh` option is not a missing auxiliary input for these rows. Source header/implementation hashes, config/spec/start/runner bindings and unstarted-versus-observed status are retained. This performs no interconnect sweep, parser change, configuration change or new simulation.

The [v2 startup coverage audit](review_pack/interconnect_identity_v2) extends observations to all41 already-started rows, including the eight subsequently admitted Gaussian/LUD/NN rows. All41 startup mode/explicit inline options match their immutable effective configurations; the earlier33 config/spec/start/runner identities and both pinned Core source hashes are unchanged. The three forbidden Hotspot labels remain unstarted and configuration-only. Exact option lines and bounded prefix observation hashes are retained; these are not whole-log final hashes or terminal acceptance. No new row, input, configuration, execution path or scientific promotion follows from this CPU identity audit.


The separately [admitted source-profile HotspotV2 input](review_pack/hotspot_derived_admission_v1)
has five new-input arms with common32768 lower cap, input and platform, and
separate conventional/finite Core/binary identities. Their complete [terminal
and resource balance receipts](review_pack/hotspot_derived_complete_v1) pass.
Its PRIMARY_RESIDENCE_AND_OCCUPANCY.tsv exposes IO256/OO128 descriptive metrics:
both retire 117,304 cacheable warp instructions and collect 695,640 32B sectors,
with the existing64×cycle denominator and exact residence decomposition.
Unequal active depth does not isolate ordering. No new matched128/WAIT128 arm
was registered. All ratios use only these five new-input receipts; no old
baseline or original Hotspot result is relabelled. Reconstruction scope does
not certify original ELF/native execution or resolve the original input HOLD.


Final original execution closure,2026-10-16T21:33Z:41 started rows strictPASS,
three original Hotspot rows remain unstarted admissionHOLD. Eleven primary
trios are numerically complete, retaining all regressions, especially GESUMMV
C+99700244/OO142770419/IO193506220cycles. Full-body3145856 cacheable warp
retirements and38797824 collected32B sectors match in both finite arms. Their
IO256/OO128 descriptive metrics do not become a matched-depth claim. Original
Btree/2D/LUD format pending and original Hotspot HOLD remain. The six separate
conditional Btree E-list arms also close strict/resource/matched128 within
that one new bundle; original denominators and capture/native/area equivalence
are not imported. No cohort aggregate is produced. See final_closure_v1.
