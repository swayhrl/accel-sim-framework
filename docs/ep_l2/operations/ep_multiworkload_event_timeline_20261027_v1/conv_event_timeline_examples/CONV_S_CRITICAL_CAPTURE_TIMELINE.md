# Conv S critical R8 capture and frontend rejection

The existing portable wrapper rendered the accepted Conv raw in0.681s withRC0, using exact expected names from the frozen whole-command input binding and actual accepted UID1/2catalogue. UIDs were joined by accepted order/name, not guessed from ordinals. Output is8192retained events and8files/16046734B in CONV_S_EVENT_TIMELINE. This is a strict wire/display component, not a new Source/input/application qualification. The frozen package, sources, raw, case and accepted point were not changed.

## What the fourth slot actually captures

The fourth snapshot is present: slot3, rank1 FULL_NEW, slice57/set7,8reserved ways, triggerUID156198 atordinal775135/CORE6903. It is not rank2 PRODUCTION_TAGFAIL. The earlier scope audit explains why the later actual-ft_access failure counter remains0: the frontend filters these requests before calling access().

| Actual event | UID | Ordinal | CORE | L2 edge | DRAM edge | Recorded evidence |
|---|---|---:|---:|---:|---:|---|
|FRONTEND_WAIT|156198|775134|6903|6903|5183|aux4 = bit2 TAG_SET_PENDING|
|PRESSURE_NEW|156198|775135|6903|6903|5183|aux34359738376 = ways8/R8|
|FRONTEND_WAIT|156198|775747|6904|6904|5184|same exact UID/set/address, aux4|
|PRESSURE_NEW|156198|775748|6904|6904|5184|same exact UID/set/address, R8|

This matches an actual capped R4SAMPLE for slice57/set7/UID156198/CORE6903. That source emits pressure samples only after raw==RESERVATION_FAIL (gpu-cache.cc3129-3146), so the sample supplies a same-request rawFAIL witness; it is not a product of two aggregate counts. Independently, each captured WAIT mask is the actual cached production-plan TAG_SET_PENDING bit (ep-l2-ft-cache.inc194-215; mechanism-interface.h WaitReason index2), and the immediately following pressure event recordsR8. The wire's PRESSURE_NEW kind itself does not contain a separate raw-status field; do not rename it PRODUCTION_TAGFAIL.

## Retained wait, with a censored endpoint

The same UID has206WAIT and206R8pressure records, one exact pair for every consecutiveL2/CORE6903through7108, all wait-ordinal+1==pressure-ordinal. There is no ADMIT_DECISION, FRONTEND_COMMIT or RESPONSE_ACCEPT for that UID in this capture. The last pair is887798/887799 atCORE7108/L2edge7108/DRAMedge5337.

The first-to-last recorded rejection spans205COREcounter boundaries, comprising206observations. It is not a measured complete request latency. The request's ingress/birth is not retained; acceptance/finish is right-censored. The snapshot contains no targetset7Tag mutation after the trigger anchor, so it does not show which later completion freed a way. Do not infer that the request never succeeded later in the completed application.

Snapshot3bounds are CORE6844-7108, ordinals742571-887838, pre512/post1536. pre_lost11418declares overwritten earlier slice history. post_complete1 means the1536event quota was recorded; it does not close this request's wait. CRITICAL_UID156198_RETAINED_EVENTS.csv has all412actual UID records; CRITICAL_UID156198_R8_PREREJECT_JOINT.csv has the206strict same-head pairs.

## Cross-domain ordering is explicit

| Actual event | UID | Ordinal | CORE | L2 edge | DRAM edge |
|---|---|---:|---:|---:|---:|
|PRESSURE_NEW target57/7|156198|775135|6903|6903|5183|
|LOWER_DEQUEUE|119792|775380|6904|6903|5184|
|DRAM_DELAY_ENQUEUE|119792|775381|6904|6903|5184|
|DRAM_MC_PUSH|113514|775382|6904|6903|5184|
|L2_INGRESS|188697|775743|6904|6904|5184|
|FRONTEND_WAIT target57/7|156198|775747|6904|6904|5184|

CORE6904contains a DRAM-domain stage with the previous L2edge6903and then the L2domain stage atedge6904. Recorded ordinal preserves this order; it is not physical time. Other packets continue moving while this frontend head is blocked. The MC packet's set is UNKNOWN in the wire and is not assigned to targetset7 by an address lookup or conjecture.

Packet119792also has a complete retained fixed-queue pair: enqueueCORE6904, auxdeadline7004at both endpoints, actualMCpush7006; observed queue endpoint difference102CORE and push-after-deadline2CORE. It is a separate packet, not the stalled UID. No whole-population timing or credit/bank-conflict attribution follows from this example. CORE/L2/DRAM counters stay in their own domains; the VCD's ordinal axis must never be converted to physicalns/ps.

## Coverage and N/A boundaries

Global META full_new42717equals the earlier rawFAIL/R8head observation total, while actual production_fail0belongs to the later access hook. full_trigger_not_captured42511and trigger_capacity_miss593768show that most later high-pressure notifications did not receive a retained window. The source did preserve the first fullR8sample in reserved slot3; it does not promise all full/failure episodes. The other three snapshots are ordinaryR4triggers.

Formal S/FT1has no RO runtime. Retained RO event count is0, but RO eligibility/ready/retirement/fullROlifetime are N/A here, not evidence that a certified Fmechanism would have no eligible victims. Complete latency for UID156198is UNKNOWN. Tag pressure is PROVEN; T performance benefit and end-to-end causality remain UNKNOWN.

All exact hashes/catalogue provenance, resource readbacks, CLI exit, view manifests and small CSVs are in this directory and CONV_CRITICAL_CAPTURE_SUMMARY.json. CPU20/nice10/AS512MiB/wall120were used; existing modelCPU16/17slots were not used. No new model, actor, scientific registration, Source/spec or accepted-result write occurred.
