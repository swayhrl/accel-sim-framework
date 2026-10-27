# Typical actual captured event timelines

Input: Main's real accepted Vector ON VERIFIED_EPET_COMPONENT.json, SHAe4e85cd8fa3ec5a057a75b6066077f0da3d2cf0475a67817c34e5ad3bf5eb445. This is read-only postprocessing of that component, not new acceptance or a model replay. All durations below are differences of recorded CORE counter boundaries, never ordinal differences or physical ns/ps.

## Coverage first

There are6144retained events in three ordinary2048-event captures. They were triggered by R4 NEW exposures; there is no retained critical capture. Captures cover slice5/set17 CORE6823-7038, slice24/set23 CORE6826-7050, and slice37/set17 CORE6857-7068. The ranges describe the slice capture, which includes endpoints for other sets too. They do not cover every set or the entire application (META ends atCORE77237). pre_lost14443/14643/14767 establishes censored prehistory. post_complete1 means1536post-events were retained; it does not mean every transaction completed in the capture.

META independently reports production_fail0 and full_new0 for its instrumented notification population, high_new44082, trigger_capacity_miss43971 and trigger_repeat108. These global observer fields are separate evidence from the selected windows; missing a TagFAIL event in the6144selected events alone would not establish a workload-wide zero. No whole-population latency, percentile, Little's Law, bandwidth, or end-to-end speed claim is derived from these pressure-selected early captures.

## Fixed-delay queue: exact same-packet endpoints

The strict join requires same non-UNKNOWN UID, slice, address, payload generation, sector mask and aux deadline, with enqueue ordinal preceding actual MC-push ordinal. Both aux fields must be the same recorded CORE ready deadline. There are130complete pairs (slice5:43; slice24:46; slice37:41). All130have deadline minus enqueue=100CORE. After the deadline,87pairs wait1additionalCORE and43wait2; observed fixed-queue residence is therefore101/102CORE, respectively. These are selected complete pairs, not a population estimate. Another114captured enqueue endpoints have no push and114push endpoints have no enqueue in retained context; their residence remains UNKNOWN, not zero.

| Packet UID | Slice/payload generation | Address/sector mask | Enqueue ordinal / CORE | Same aux deadline at both ends | Push ordinal / CORE | Deadline-enqueue | Push-deadline |
|---|---|---|---|---|---|---|---|
|382639|5/31|0x7f5f38043e80 /1|930641 /6828|6928|994853 /6930|100CORE|2CORE|
|383330|5/1|0x7f5f380755a0 /2|932574 /6831|6931|996187 /6932|100CORE|1CORE|

The residual is observed, but separating clock-domain sampling from FIFO/credit/scheduler backpressure is UNKNOWN from these endpoints. In particular, a1-2CORE residual is not evidence of saturation or a pure MC service time. The exact clocks and DRAM-edge differences remain in DRAM_DELAY_MATCHED_PAIRS.csv.

Two recorded packet tails show later endpoints without inventing their creation:

| UID | Actual endpoint | Ordinal | CORE | DRAM edge |
|---|---|---|---|---|
|382639|DRAM_DELAY_ENQUEUE|930641|6828|5127|
|382639|DRAM_MC_PUSH|994853|6930|5203|
|382639|SCHEDULER_ACCEPT|995504|6931|5204|
|382639|DRAM_COLUMN|995505|6931|5204|
|382639|DRAM_RETURN|1006026|6948|5217|
|382639|RO_READY|1006244|6948|5217|
|383330|DRAM_DELAY_ENQUEUE|932574|6831|5129|
|383330|DRAM_MC_PUSH|996187|6932|5205|
|383330|SCHEDULER_ACCEPT|997330|6934|5206|
|383330|DRAM_COLUMN|1031168|6990|5248|
|383330|DRAM_RETURN|1041191|7007|5261|
|383330|RO_READY|1041403|7007|5261|

For these two examples, enqueue-to-RO_READY is120and176CORE, respectively. Those are observed packet subspans, not complete RO transaction lifetimes. The recorded column aux64decodes to a32-byte read column (atom<<1, writebit0); it is real column issue, unlike lowerpop successful_bytes. A scheduler-accept-to-column gap is an endpoint difference, not an exclusive bank-conflict attribution. The packet creation/RO birth is outside these retained tails. All9chosen UID examples and their actual events are in TYPICAL_UID_EVENTS.csv.

## Same-CORE RESERVED peak retained

R is unknown before the first recorded pressure anchor. After it, the reconstruction uses only the actual target-set TAG_MUTATION old/new reserved masks, incrementing or decrementing the any-sector-RESERVED Tag count. Repeated pressure anchors must agree. No cache probe or all-set scan is performed offline.

| Slice/set | CORE | Actual ordinal sequence | Recorded R progression |
|---|---|---|---|
|5/17|6875|961135anchor;961136mask0->0;961137mask0->1;961138mask1->0|4->5->4|
|24/23|6883|966303anchor;966304mask0->0;966305mask0->1;966306mask1->0|4->5->4|
|37/17|6904|979442anchor;979443mask0->0;979444mask0->1;979445mask1->0|4->5->4|

These are ordered operations sharing one CORE timestamp, not separately measured physical subcycles. The peak5is real within the retained mutation sequence and remains below8ways. Across the three target sets there are12captured same-CORE4->5->4excursions, including sector re-reservations; TARGET_SET_RESERVED_EVENTS.csv preserves their individual mask/generation records and UNKNOWN pre-anchor R. Do not replace these sequences with a single tick-end value or infer unobserved peaks outside the captures.

The first target UID124366has ADMIT_DECISION atordinal961134, pressure at961135, actual FRONTEND_COMMIT961139and RESPONSE_ACCEPT961140, all CORE6875. UID133664has decision/pressure atCORE6882, repeated decision/pressure at6883, then actual commit/response at6883. Decision is distinct from actual acceptance. Packet read/write type is not encoded in this wire, and no type is guessed from its address or short response span.

## RO lifetime boundary

No retained UID has both RO_LOWER_CREATE and DRAM_RETURN, and RO_STATE is not an explicit transaction-birth event. A complete RO lifetime is UNKNOWN. The capture contains161distinct (slice,payload slot,payload generation) RO state identities and53actual RO_RETIRE records;108identities lack a retained retirement. First-observed states are left-censored birth evidence; all first-to-last durations in RO_OBSERVED_TAILS.csv are observed tails, never full lifetimes. Packet UID to RO slot is not joined by address or generation equality alone.

A concrete left-censored tail is slice5/payload314/generation1, line0x7f5f39095980, physicalset25/way2:

| Ordinal | CORE | Actual state | Required/issued/ready | Waiters | reuse_seen/eligible |
|---|---|---|---|---|---|
|927367|6823|RO_STATE|15/15/7|1|1/0|
|941352|6844|RO_STATE|15/15/15|1|1/0|
|941923|6845|RO_STATE|15/15/15|0|1/0|
|941924|6845|RO_RETIRE|15/15/15|0|1/0|

It proves those recorded masks, waiter transitions and retirement. Its observed tail spans22CORE; its birth and full lifetime remain UNKNOWN. This set25tail is not a candidate in the high-pressure targetset17, so it does not establish same-set pressure/reuse co-occurrence. TYPICAL_RO_CENSORED_TAIL.csv contains the exact records.

## Reproducibility and limits

CAPTURED_TIMELINE_SUMMARY.json records all bounds, joins, histograms, censoring,12same-CORE sequences and CSV hashes. analyze_captured_timelines.py SHA3dc1e37af5278cff4f9e4996beef679b038da0fa8b379d7a7b14161b963df90a ran once withRC0 in0.092s, CPU18/nice10/AS512MiB/wall120; output remains well below16MiB. Resource admission and a fresh pre-execution snapshot passed. Actual simultaneous model generations matched receipts: Conv PID1673529/RSS1027604480B onCPU17; GES PID1673533/RSS2097152000B onCPU16. These are readback samples, not process peaks. No model slot, Source, raw/verifiedJSON, accepted point, frozen tool/package, registry or experimental budget changed.
