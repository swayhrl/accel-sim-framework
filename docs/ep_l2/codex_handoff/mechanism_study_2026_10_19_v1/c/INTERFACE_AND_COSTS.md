# C source module contract and explicit costs

Parent Core84359d4, A interface980072bbbcbd4ad00cdf85650283931e94cad395. A owns all public cache/partition/config changes and the formal build. C has modified only new RO module/test files. CACHE_ALLOCATOR_ADAPTER.patch applies to84359d4 but is a review patch; A must adapt it once to the newer common source. Do not wholesale merge historical30c2920a and do not delete legacy mechanism refusal checks.

## Four independent controls

New CLI: gpgpu_ep_l2_ro_tag_detach=T and gpgpu_ep_l2_ro_line_mshr_bypass=M, both default0. Background is the same U_WB16/P1 with payload1168, line-MSHR128, D512, per-address32, WAD128. Old C8 tests/storage are retained as history; C mode rejects C8. T00/M00 is the same new-binary native U control. T10 uses the normal line table even after a Tag detaches; M01 keeps pending Tag until fill; T11 may create an independent same-address transaction once its Tag has detached. No unbudgeted completion address map is introduced. All states here are SOURCE_PREPARED, not runtime qualification.

T uses the historical conservative waiter-aware policy: only pending certified transactions with no observed same-line requester reuse are detachable; reuse_seen remains sticky through retirement. This adds a declared policy bit, not a future-reuse oracle. M bypass is only for complete-oracle GLOBAL_ACC_R demand requests. Synthetic write-allocate reads, writes/atomics, uncovered lines and uncertain inputs remain native. A certified-line writer is a certificate violation and must fail closed; it cannot quietly make an invalid oracle appear correct.

## Storage and lookup accounting

| Item | Binding/cost |
|---|---|
|128B data|Exactly1168 paid slots in existing four-bank store; no second payload RAM|
|Requests|Native D512 free-list only; every normal and RO descriptor shares it and holds ownership until accepted response; capacity test mixes384RO+128native|
|Line records|Native128 table in00/10; skipped on a new certified transaction in01/11; attached Tag/Payload allows merging, T-only may find detached ownership through native line table|
|Per-address cap|Same32 across normal and RO descriptors; bounded scan of the existing shared descriptors, no new address-indexed table|
|Completion metadata|At most one control entry per physical landing; line/epoch, Tag binding+generation, required/issued/ready4-bit masks, waiter descriptor identities, prepared-cycle metadata. Waiter chains store descriptor handles only; request pointers and sector masks are retrieved directly from the original sharedD512 records. There is no second requester/mask record array or independent admission pool. Total live waiters remains bounded by D512|
|Additional shared descriptor fields|RO-external flag, owner line and generation; generation is retained across native reuse. Software types are bool, new_addr_type and unsigned long long. Exact ABI sizeof and physical implementation/PPA are UNKNOWN until build/design; no old R3 area claim|
|Tag safety|One uint64 generation per Tag plus existing payload handle. Old return writes only its checked payload generation; detached return never invokes Tag-ready callback|
|RO lookup|A timed frontend hook launches one query per slice per physical GPUcycle; ready at query_issue+1. One cached frontend ticket only. Query covers the bounded shared descriptor/attached Tag lookup; parallel comparison/control cost is explicit, not a free extra address map. Preview is immutable; source observer scans do not grant data or change arbitration|
|Data services|Real RO fill WRITE and response READ arbitrate against the same P1 physical banks. Native lower/return/response queues and backpressure remain. A denied response must reread on a later granted cycle; no hidden response data buffer|
|Observations|One current frontend-head UID and a reason bitset plus bounded histograms, not an unbounded per-access map. Count first blocked request/reason, first-to-accept duration and pending head. Reasons and slices overlap and cannot be summed into GPU stalls|
|Duplicate traffic|Count actual accepted lower sectors and concurrently duplicated sectors/bytes, actual avoided line allocations, admitted/merged/completed requests and peaks. This is not a shadow hit estimate or an application speedup|

Resource counters are EPL2ROC1 RESOURCE/WAIT plus EPL2ROV1. Actual distinct-address occupancy beyond a Tag/line lookup needs a measured opportunity observer; no unique-address count is fabricated from transaction count.

## Required A integration

1. Apply new RO modules and ep-l2-ro-mshr.inc, then adapt CACHE_ALLOCATOR_ADAPTER.patch to the A-owned common cache files. Keep current atomic callbacks, quota/RG1/MQ2 fixes, bank clocks and default-OFF behavior. The patch preserves those source bodies and retains the old rejected legacy feature options.
2. Register T/M and manifest/range/scope options defaultOFF. Require separate U16/P1 mode, D512/line128/address32/WAD128. Reject unqualified mixes with B victim, A diagnostics, S64, quota, P2, MQ2/RG1 and old Ideals. The source guard covers all options already present in84359d4; A adds its newly introduced options.
3. Bind the exact complete commandlist hash at GPU/partition entry, drain prior work, begin once before the first kernel, and end only after the whole commandlist and all native/RO queues drain. Never end/restart at a kernel boundary. The required hooks already exist in the historical30c2920a interface, but are not inherited into84359d4 by adding headers.
4. ro_frontend_cycle(mf) is a timed hook before native preview, not a resource allocation in preview. The patch inserts it at the actual partition head. Direct native-cache fixtures call the same hook and wait only for ep_l2_ro_lookup_wait; they do not hide capacity refusals.
5. Route flagged return packets by payload_id/generation before ordinary Tag fill; lower acceptance invokes the module only after real queue acceptance. Preserve actual response READ grant/same-cycle enqueue and pins. Include RO ownership in drain/consistency checks.
6. Add CMake native targets for tests/ep_l2/test_ro_runtime.cc, test_ro_partition.cc, test_ro_transactions.cc, test_ro_store_port.cc, test_ro_oracle_certificate.cc and test_ro_bank_progress.cc; assertions enabled. Bind exact common compiler/headers/libraries and use E's admission. Print ro_print at final application terminal.

Host prefill is range-aware: initial initialization is allowed. During the active whole epoch, overlap with certified lines refuses; unrelated lines remain eligible only after native clean/quiescent checks. Pending/dirty/pinned ownership must refuse before mutation. Once the whole epoch ends, later clean/quiescent prefill is allowed. No initial-only blanket restriction, producer clock reset, dirty discard or synthetic bank cycle is introduced.

## Combined native and RO acceptance counters

This RO mode still executes the real L2/64-slice pipeline and real lower memory.
It must pass physical bank, WAD, actual version/return and all global requester
closure gates; physical cache/WB scope is not N/A. Native m_ft_read_refs and
mshr descriptor response lists contain ordinary native requests; RO pins and
responses are owned by the same-D512 external descriptors and module. Check
native responses plus RO responses against total admitted requests, shared
free-list count against combined occupancy, all RO live/sector/prepared state0,
and the unchanged partition-level request-tracker/ICNT/DRAM queues drained. Do
not mistake a native-only subcounter for the combined total or waive the global
terminal checks. Native bank operations include the newly labelled RO clients.

Literal source encoding adds RO as the fifth payload-role label and two states
beyond the eight old states: uncompacted role/state labels therefore need at
least3/4 bits respectively. This is a control-encoding requirement, not a new
payload data array or a synthesized area number. Shared descriptors additionally
hold the RO-external marker, owner line and generation; completion chains carry
only descriptor identities. Request pointer/sector fields live exclusively in
the original D512 records. C explicitly removed duplicate waiter pointer/mask
storage. Full PPA and concrete ABI sizeof remain unmeasured.

The whole-epoch parser follows runtime Framework197741b's trace_parser.cc:
mem_width is only the memory-presence flag; actual width is decoded from opcode,
as the native parser does because NVBit can report a wrong width. Address
compression/mask and complete grid/warp coverage are checked; the parser does
not rewrite a trace or its opcodes.
