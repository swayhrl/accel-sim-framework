# POST-FAST64 Lane D — Observer Telemetry and Diagnostic Execution Handoff

Status: **READY TO START — Lane D is now scientifically justified by reviewed Lane B/C gaps**

## 0. Frozen authorities

Accepted FAST64 remains immutable:

- Framework: `hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`
- terminal state: `FAST64_COMPLETE_READY_FOR_REVIEW`

Post-FAST64 planning authority:

- `hrl/decoupled-l1-fast64-post-analysis-v0`

Reviewed lane checkpoints that define Lane-D inputs:

- Lane A: `hrl/post-fast64-paper-v0@c1774a452e244d431c215010b1039e9d3e074f2a`
- Lane B: `hrl/post-fast64-physical-causal-v0@757b8cbf2c536b04f8a6ef4db847af04f337378d`
- Lane C: `hrl/post-fast64-duplicate-miss-v0@18800873478576309b08b538974c3872fc2cb6df`

Formal Core parents:

- non-2D observer parent: Core95 `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`
- 2D observer parent: Core658 `6587238c60214d99491f4048e28ce8a3458c1509`

Every Lane-D simulator row is `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`. No Lane-D row may replace an accepted FAST64 cell, enter GM-FAST12, or mutate FAST64.0-.7 PASS evidence.

## 1. Reviewed scientific gaps that authorize Lane D

Lane B source audit already rules out direct physical-ID/free-list effects on lower address, L2 set/partition mapping, and request ordering. Do not spend runs on that hypothesis.

Lane B existing-data analysis shows a workload-local measured pattern for BICG/GESUMMV: as physical pool grows, normalized front-end no-free exposure can fall while L2 miss/reservation pressure and cycles rise. This is stronger than a null result but is not causal proof. The universal statement that every workload transfers pressure downstream is not supported; Btree is a control counterexample. Lane D must distinguish:

- universal H2: not supported;
- BICG/GESUMMV local H2: `MEASURED_CORRELATION`, causality unresolved pending occupancy/lifetime telemetry.

Lane B/C leave these exact causal arrows unresolved:

`pool -> admitted/inflight pressure -> L2 pressure -> pending lifetime -> pending Tag eviction -> duplicate traffic -> performance`

Lane C already source-proves PAPER_IO duplicate semantics and quantifies accepted FAST12. The unqualified dissertation claim that duplicate requests are always rare is not supported on FAST64/PAPER_IO. Lane D is authorized to extend the same semantics to OO and to measure lifetime/occupancy needed for the physical-pool explanation.

## 2. Lane-D stage state machine

`D0_AUTHORITY_AND_COVERAGE_FREEZE`
`-> D1_TELEMETRY_SEMANTICS_FROZEN`
`-> D2_OBSERVER_IMPLEMENTED_AND_UNIT_TESTED`
`-> D3_OBSERVER_EQUIVALENCE_PASS`
`-> D4_PHYSICAL_TELEMETRY_WAVE`
`-> D5_OO_DUPLICATE_FAST12_WAVE`
`-> D6_INTEGRATED_OBSERVER_ANALYSIS`
`-> D7_OBSERVER_CLOSEOUT`
`-> D_OBSERVER_EVIDENCE_READY`

D0-D3 are HARD prerequisites for using any new simulator telemetry scientifically. D4 and D5 may execute physically in parallel after D3 when resources permit.

## 3. D0 — Authority and coverage freeze

Before source modification:

1. fetch all remote branches;
2. bind the exact FAST64/A/B/C commit SHAs above;
3. read:
   - `POST_FAST64_MULTI_GOAL_CONTRACT.md`;
   - `POST_FAST64_LANE_HANDOFFS.md`;
   - Lane-B `PHYSICAL_POOL_CAUSAL_HANDOFF.md`;
   - Lane-B `LANE_D_TELEMETRY_REQUIREMENTS_FROM_LANE_B.md`;
   - Lane-C `DUPLICATE_MISS_HANDOFF.md`;
   - Lane-C `DUPLICATE_MISS_SOURCE_SEMANTICS.md`;
4. inventory existing post-FAST64 runs and do not duplicate exact live/terminal telemetry rows;
5. write a compact authority/coverage manifest.

HARD:

- accepted FAST64 commit/hash boundaries match;
- Lane-B/C handoff commits match exactly;
- every planned row has one owner and one disposition;
- no accepted FAST64 result path is writable by Lane-D collectors.

Suggested output:

`docs/dtc_l1/post_fast64/generated/D0_OBSERVER_AUTHORITY_MANIFEST.tsv`

## 4. D1 — Freeze exact observer semantics

Instrumentation must be observation-only. Observer state must never affect lookup, victim choice, allocation/free selection, admission, retirement, reclaim, lower scheduling, completion, assertions, or simulator termination.

### D1.1 Common IO/OO alloc-to-ready latency

Counters:

- `DTC_L1_{io,oo}_alloc_to_ready_count`
- `DTC_L1_{io,oo}_alloc_to_ready_sum_cycles`
- `DTC_L1_{io,oo}_alloc_to_ready_max_cycles`

Semantics:

- on each successfully committed `NEW_MISS`, record allocation cycle keyed by exact `{physical_id,generation}`;
- on matching successful completion, accumulate `complete_cycle - allocation_cycle` exactly once;
- do not count no-free/allocation-width retries, hits, stale fills, or a recycled identity;
- terminal observer map must drain to zero.

Purpose: close `L2/downstream pressure -> pending lifetime` evidence gap.

### D1.2 Pending Tag eviction count

Counters:

- `DTC_L1_io_pending_tag_evictions`
- `DTC_L1_oo_pending_tag_evictions`

Increment exactly when a valid logical Tag victim is replaced while its generation-qualified physical allocation is not ready. Do not infer this from total Tag evictions.

Purpose: close `pending lifetime -> pending Tag eviction` denominator gap.

### D1.3 IO pending-eviction to original-response latency

Counters:

- `DTC_L1_io_pending_eviction_to_response_count`
- `..._sum_cycles`
- `..._max_cycles`

On a pending IO Tag eviction, record eviction cycle keyed by victim identity. On the original matching response, accumulate response minus eviction cycle. Cleanup only on exact id+generation completion.

Purpose: measure the exposure interval in which a same-line reaccess can become a duplicate.

### D1.4 OO deferred Tag-eviction to final reclaim latency

Counters:

- `DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_count`
- `..._sum_cycles`
- `..._max_cycles`

On OO Tag eviction with `ref_count > 0`, record cycle keyed by victim identity. On matching final-reference reclaim/release, accumulate elapsed cycles exactly once. Immediate zero-ref reclaim is excluded.

Purpose: close the H4 reclaim-lifetime gap.

### D1.5 Exact OO duplicate-after-eviction observer

Counter:

`DTC_L1_oo_duplicate_after_eviction`

Match the already source-proven IO meaning, without changing OO behavior:

1. when a valid OO Tag is evicted while its physical line is pending, record observer-only `(logical_line, physical_identity)`;
2. erase that record when the exact original id+generation completes;
3. if the same logical line later commits a successful `NEW_MISS` before original completion, erase the matching observer record and increment once;
4. do not count a pending Tag hit, post-response reaccess, allocation retry, or stale/recycled identity;
5. the normal mechanism must independently create the lower request; observer state cannot cause it.

Purpose: extend the dissertation 4.2.2 duplicate-request characterization to OO.

### D1.6 Time-integrated physical/inflight occupancy

Lane-D must add a source-correct time-integral rather than infer occupancy from retry counts.

Preferred per-mode aggregate families:

- `DTC_L1_{io,oo}_observer_sample_sm_cycles`
- `DTC_L1_{io,oo}_physical_allocated_line_cycles`
- `DTC_L1_{io,oo}_physical_full_sm_cycles`
- `DTC_L1_{io,oo}_inflight_request_cycles`

Semantics:

- sample exactly once per active SM simulation cycle at a source-proven once-per-cycle hook;
- `physical_allocated_line_cycles += currently allocated physical lines`;
- `physical_full_sm_cycles += 1` iff allocated lines equal configured physical capacity;
- `inflight_request_cycles += current DTC lower in-flight request count`;
- sample count increments once at the same hook.

If `ldst_unit::cycle()` is not source-proven to provide exactly one sample per active SM simulation cycle, Codex must find the correct hook before implementing and must not mislabel an opportunistic-access sample as an SM-cycle integral.

Derived later, not inside mechanism code:

- average physical occupancy = allocated-line-cycles / sample-SM-cycles;
- pool-full fraction = full-SM-cycles / sample-SM-cycles;
- average in-flight lower requests per SM = inflight-request-cycles / sample-SM-cycles.

Purpose: directly test `pool -> admitted/inflight pressure` and distinguish retry event counts from time exposure.

### D1.7 Optional queue integrals

Only if source inspection shows they are low-risk and directly useful, Lane-D may also sample lower-create / lower-issue queue occupancy. Do not expand telemetry merely because implementation is convenient.

D1 HARD:

- each counter has event location, key, cleanup point, units, and unresolved scientific arrow documented;
- no observer field participates in mechanism control flow;
- no unsupported proxy is introduced.

Output:

`docs/dtc_l1/post_fast64/LANE_D_OBSERVER_COUNTER_SEMANTICS.md`

## 5. D2 — Isolated implementation and unit tests

Use isolated Core branches/worktrees only:

- `hrl/dtc-l1-post-fast64-observer95-v0` rooted exactly at Core95;
- `hrl/dtc-l1-post-fast64-observer658-v0` rooted exactly at Core658 when 2D telemetry is needed.

Do not modify formal Core95/Core658 branches.

Required directed tests include at least:

### OO duplicate tests

- positive: pending Tag evicted -> same-line successful NEW_MISS before original completion -> exactly +1;
- pending-hit negative: Tag still present/non-ready -> no duplicate;
- post-response negative: pending Tag evicted -> original completion -> same-line NEW_MISS -> no duplicate;
- generation negative: recycled physical id cannot match stale observer identity;
- allocation retry negative: no-free/allocation-width retry alone cannot count duplicate.

### Lifetime tests

- one alloc->ready interval gives exact count/sum/max;
- stale/mismatched completion cannot close a different generation;
- pending eviction->response interval closes once;
- OO deferred eviction->final reclaim interval closes once;
- immediate reclaim is excluded from deferred lifetime.

### Occupancy tests

Use a deterministic synthetic sequence or a source-defined unit fixture to prove sample count, allocated-line integral, full-cycle count, and in-flight integral arithmetic.

D2 HARD:

- all existing DTC tests still pass;
- new observer tests pass;
- terminal observer maps have no leaked live identity in unit fixtures;
- source diff contains no intended mechanism semantic change.

## 6. D3 — Observer-equivalence gate

No expensive diagnostic wave may be interpreted before D3 PASS.

For Core95 observer qualification, use cheap exact accepted controls where possible. Minimum required coverage:

- NN PAPER_IO and PAPER_OO primary configuration;
- Btree PAPER_IO and PAPER_OO using an exact accepted primary or physical-32 configuration;
- one cheap Base control if observer plumbing touches common printing/stat aggregation.

A fresh parent run is unnecessary when an exact accepted parent row has matching config/payload/Core/runtime and immutable terminal evidence; otherwise run the minimum parent control needed.

For each observer row compare against its parent/reference:

- cycles: exact;
- instructions: exact;
- every pre-existing scientific counter emitted by the compact parser: exact;
- L1/L2/global traffic counters: exact;
- lower create/issue/response and credit accounting: exact;
- dependency accounting: exact;
- terminal PIB/inflight/lower/ref drains: exact;
- only new observer counters may differ by presence/value;
- host wall time/RSS need not be exact and are not scientific equivalence criteria.

If any pre-existing simulated result differs, this is an observer bug until source-classified. Fix it; do not use the telemetry.

For Core658, the first retained 2D OO observer run may serve as observer-equivalence qualification only if all pre-existing metrics match the accepted Core658 2D OO reference exactly. If not, fix before retaining its new counter.

Outputs:

- `generated/post_fast64/D3_OBSERVER_EQUIVALENCE.tsv`
- `LANE_D_OBSERVER_EQUIVALENCE.md`

Terminal gate:

`D3_OBSERVER_EQUIVALENCE_PASS`

## 7. D4 — Physical-pool telemetry wave

After D3 PASS, run the minimum high-information matrix under the Core95 observer:

Workloads:

- BICG
- GESUMMV
- Btree

First-wave physical points:

- 24 KiB
- 32 KiB
- 48 KiB

Modes:

- IO
- OO

This is 18 possible rows. Do not rerun an exact row if an equivalent observer-telemetry row already exists.

Use the exact frozen Stage6 payload/config semantics except for the observer Core/runtime identity. Preserve requested and modeled capacities.

After enough first-wave rows terminate, automatically analyze whether 40-KiB data can discriminate H2/H3/H4. Launch 40-KiB only when scientifically useful; do not add it just to make the matrix rectangular.

Every row must have immutable/fresh execution identity, natural terminal or a source-classified expected boundary, strict pre-existing accounting/drain, and classification `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.

Required D4 derived outputs by workload/mode/point:

- average physical occupancy;
- pool-full fraction;
- average in-flight lower requests;
- average/max alloc->ready latency;
- pending Tag evictions and rate;
- IO duplicate count/share and pending-eviction response latency;
- OO deferred-reclaim average/max lifetime;
- L2 miss/reservation pressure normalized by lower requests and instructions;
- cycles/instruction and same-mode performance normalization.

D4 must not infer causality automatically.

## 8. D5 — OO duplicate FAST12 exploratory wave

After D3 PASS, quantify the OO analogue of the dissertation 4.2.2 issue on the frozen FAST12 workload roster.

Use primary FAST64 OO configuration/payload semantics. Use observer95 for non-2D workloads and observer658 for 2DConvolution. Preserve exact parent/reuse authority in a manifest.

If resources are ample, launch all 12 nonduplicate OO rows dynamically. If resource admission requires prioritization, use:

1. high-duplicate IO exceptions: Gaussian, 2DConvolution, GEMM, LUD;
2. IO-regression / moderate-duplicate workloads: ATAX, BICG, GESUMMV, Hotspot1;
3. controls: Btree, DWT2D, NN, MRI-Q.

For each OO row report:

- lower-created;
- pending hits;
- Tag evictions;
- new `oo_duplicate_after_eviction`;
- duplicate share of lower;
- duplicate per Tag eviction;
- if denominator is meaningful, duplicate/(duplicate+pending-hit) as a descriptive event ratio only;
- source-proven duplicate lower-request payload bytes only if lower request remains 128-B whole-line in that mode/config;
- no claim of DRAM-byte inflation unless downstream evidence proves it.

Lane C accepted IO data remains the IO authority; do not rerun IO merely to reproduce an already accepted counter unless required for observer qualification.

## 9. Duplicate traffic presentation required by integration

In addition to Lane-C `duplicate_share_of_lower = duplicate / lower_created`, integration must expose:

`duplicate_traffic_inflation = duplicate / (lower_created - duplicate)`

This answers how many duplicate request payloads are added per non-duplicate lower request. Handle zero denominator explicitly. It is a request-payload inflation ratio, not a DRAM-traffic or total-link-traffic ratio.

Do not rewrite Lane C accepted analysis; create a post-review derived extension with exact provenance.

## 10. D6 — Integrated observer analysis

Use Lane A/B/C accepted-derived outputs plus D4/D5 telemetry.

For each arrow below assign exactly one of:

- `SOURCE_PROVEN`
- `MEASURED_CORRELATION`
- `NOT_SUPPORTED`
- `INSUFFICIENT`

Chain:

`physical pool`
`-> physical occupancy/full exposure`
`-> DTC lower in-flight concurrency`
`-> L2 miss/reservation pressure`
`-> alloc-to-ready pending lifetime`
`-> pending Tag eviction`
`-> duplicate lower traffic`
`-> performance`

Also separately analyze:

`OO Tag eviction -> deferred physical lifetime -> final reclaim -> exposed concurrency/performance`

Required review correction for H2:

- do not mechanically carry forward Lane-B's single `DATA_DOES_NOT_SUPPORT` label as the final local conclusion;
- retain that the universal cross-workload H2 is not supported;
- explicitly test the BICG/GESUMMV local hypothesis using D4 occupancy/inflight/lifetime telemetry;
- Btree remains a control workload.

For duplicate traffic, determine per workload whether it is best described as negligible, measurable-secondary, or potentially major, but do not use an after-the-fact threshold as a theorem. In particular, duplicate traffic may be a feedback/amplification mechanism while downstream L2 pressure remains the dominant performance limiter.

## 11. D7 — Closeout

Required outputs:

- observer source-diff and runtime identity manifests;
- D3 equivalence package;
- D4 physical telemetry table + provenance;
- D5 OO duplicate FAST12 table + provenance;
- derived duplicate traffic-inflation extension;
- integrated arrow-classification table;
- `LANE_D_OBSERVER_FINAL.md`;
- raw-run index only, no multi-GB raw output in Git.

D7 PASS requires:

- D3 exact observer-equivalence PASS;
- every retained D4/D5 row strict-valid or explicitly source-classified nonnumeric boundary;
- no accepted FAST64 artifact modified;
- no unsupported causal arrow promoted;
- all negative/nonmonotonic outcomes retained;
- observer maps/counters have clear terminal disposition;
- output is ready for Lane-E coordinator integration.

Terminal state:

`D_OBSERVER_EVIDENCE_READY`

## 12. Resource and problem-solving policy

Use fresh dynamic admission. CPU count alone is not the gate. Check physical-core placement, cgroup quota, RSS p95/max, MemAvailable/headroom, sustained swap-out, PSI/OOM, I/O and output space.

Researcher disk floor remains projected post-wave free >= 10 GiB. Filesystem percent-used alone is not a rejection reason.

This is Goal mode. Ordinary failures must be solved rather than returned to the researcher:

`OBSERVE -> REPRODUCE -> CLASSIFY -> SOURCE INSPECT -> SOURCE-CORRECT FIX -> REGRESS -> INVALIDATE ONLY AFFECTED EXPLORATORY DATA -> RERUN ONLY AFFECTED WORK -> RESUME`

Do not stop for build/parser/path/controller/resource-admission/single-row failure/negative result/rejected hypothesis/one uninformative counter. Pause only for the true researcher boundaries in `POST_FAST64_MULTI_GOAL_CONTRACT.md`.
