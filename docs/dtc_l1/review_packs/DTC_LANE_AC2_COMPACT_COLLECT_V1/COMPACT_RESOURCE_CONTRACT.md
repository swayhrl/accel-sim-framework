# AC2 resource feasibility contract — SCIENTIFIC STOP

Authority: DTC_LANE_AC2_COMPACT_COLLECT_WB_PIPELINE_174_V1; original174 only.
Inputs are Core83aca449135703c176cfab29ae43e1245d00a557 and
Framework134a77798a2502a308c7f1e439a8f39dbc3ee043. Parent AC resource and data-path
contracts remain authoritative; X2e32afdcf is an ancestor. No AG/AD/AE integration.

Requested data budget: two4096B banks,128 raw32B sectors per bank,8192B/SM,
524288B at64SM. Actual AC2 production data bytes added relative to AC: **0**.
Compact is **NOT IMPLEMENTED**. Production remains the parent's two81920B banks,
163840B/SM additional to the original physical pool; no8KiB production claim.
The small banks exist only in a test-local capacity witness.

Exact demand is S=sum(popcount(reference.sector_mask)) over the original grouped
128B references, after full admission. Physical lifetime is not changed by S.
Duplicates within one logical128B reference are ORed by group_128b_references;
unique-sector order is existing reference order then ascending sector bit.
No PIB descriptor or original physical array is charged as new raw payload space.

The accepted AC contract retains every collected raw sector until successful WB.
Original service_entry permits WB only after sectors_left=0 and
cycle>collect_done_cycle. Therefore immediately before WB a single owner needs
32*S retained data bytes, regardless of whether another instruction overlaps.
WB denial extends this requirement; it does not reduce it.

128 sectors require4096B and exactly fit one proposed bank.129 require4128B and
cannot own just one4KiB bank. Draining both owners and allowing a *hypothetical*
serial owner to span both banks covers at most256 sectors.257 require8224B;
512 require16384B. Backpressure with no storage-release event cannot finish such
an instruction. Routing either case through original serial timing counters does
not supply a hardware buffer. Counts are not loaded values and cannot waive this
resource invariant.

The CPU source-API witness uses real memory_coalescing_arch, set_addr<=8 per lane,
its explicit unaligned cross-sector path, issue, LDST, RFU and completion/return
paths.512 requested sectors become256 references and fully admit/drain on parent
AC. This proves accepted source/API timing-domain reachability, **not** that an
executed scalar SASS instruction or a real trace produces this pattern. Fullpool
stress is separately labeled manual pre-coalesced640-reference input, not ISA
reachability. The parent published contract conservatively accepts the entire
640-line pool bound; silently narrowing it to a scalar workload subset is not an
approved fallback. The independent source-format/value/routing proof is absent.

Given this domain and unchanged retain-all-raw semantics, the fixed8KiB budget
and finite-progress requirement do not close. Scientific STOP is the authorized
outcome. No compact flag, fallback, third bank, payload borrowing, early Ref
release, reduced sector mask, new port, or altered timing comparison is installed.
