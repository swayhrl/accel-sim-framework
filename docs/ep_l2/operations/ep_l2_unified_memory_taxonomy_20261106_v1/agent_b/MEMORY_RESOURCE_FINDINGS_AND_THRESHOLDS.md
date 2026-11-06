# Memory service, native pressure and RO applicability: Agent B

This is an evidence classification and proposed experiment selection, not a new scientific acceptance. New full applications: 0; science budget consumption: 0. No raw or Trace body was scanned. Frozen small JSON/bundles and the literal small ordered commandlists were read.

## What the current evidence supports

- Vector4M has a genuine same-Source78 memory-service response: increasing modeled DRAM clock 850 to 1020 MHz changes S77184 to65522 (-15.109%) and F77237 to65797 (-14.812%), with all other effective options identical. Yet native LineMSHR peak110/S andfull0, Victim read responses0, and the Source812/1700 pressure policy never activates. Its 18.775% F cost reduction (55925 to45425) avoids eager RO service, not a faster active-RO mechanism. Memory sensitivity does not imply EP opportunity.
- Vector6M admits1,500,000 RO requesters andmerges1,124,891 (74.993%); native Sline peak110/full0. Old F112617 vsS112272 is slightly worse. It is a traffic-rich streaming contrast, not established RO pressure.
- SGEMM has1,135,915 acceptedRO and1,054,333 merges (92.818%); native line peakS34/F43 andfull0. OldF357466 vsS353921 is worse. A high merge ratio alone neither proves resource saturation nor predicts Source812 activation.
- Conv3072 has actual LineMSHR128 saturation: S6499 andF2986 full events, descriptor peaks420/409 withfull0. It responds to850->1020 service change by6.300%/7.038% S/F. Source78 F335088 is worse thanS331234. It is the first pressure-RO cross-workload candidate because the selection uses actual saturation rather than speedup. OldF had14detaches and1 concurrent duplicate sector; these are retained historical observations, not Source812 correctness qualification. The old matrix and sealed bundle agree on duplicate1.
- Scan has actual LineMSHR128 saturation: S911/F4677 full events. Source78 F admits14,536,577RO, transactions3,721,306, merges10,815,271 (74.400%), detach0/duplicate0. F2224142 vsS2162540 is worse. This is a longer, multi-kernel independent pressure case. Memory service sensitivity remains UNKNOWN: no matching isolated clock experiment exists.
- SRAD_v1 S hasLine128/full42193. Its missing F/RO/input closure prevents classifying RO applicability or issuing a ready RO experiment. Ordinary native pressure alone is not enough.
- BlackScholes has zero observed response to the same modeled850->1020 perturbation. This is bounded service insensitivity for that input/configuration; it is not a universal compute-bound label.

The machine output covers all103 original rows/slots. Only27 have Source78 reference endpoint feature measurements (57 endpoints); three inputs have a matched clock response. A complete classification view is not complete measurement coverage.

## Source812 activation contract

Read-only production path: track_b_fullf/core/src/gpgpu-sim/ep-l2-ro-runtime.inc lines114-123.

SET occurs only in actual timed frontend, after directory_ready, for a certified demand candidate whose indexedTag probe isnotHIT and either RESERVATION_FAIL or current nativeLineMSHR count>=128. Before activation, candidates use bounded native service. The one control bit is sticky for the whole commandlist epoch. Paid TVD/RO frontend tickets, queryport and full oneGPUcycle latency remain. RO merge, RO transaction count, descriptor peak, aggregate lower payloadbytes and Victim hits are not activation predicates.

Source78 saturation makesConv/Scan plausible, not guaranteed. Source identity, ownership and admission trajectory change; a future Source812 input must actually observe a certified head at pressure after directory readiness. The old per-slice max128 may have occurred on another request class or at another time. Tag-reserved pressure is UNKNOWN without the joint typed observation; do not substitute arbitrary Tag occupancy or detach count.

## Metric semantics and thresholds

No EP speedup defines a class. Actual observed full-event count>0 labels saturation; count0 labels no saturation observed for that exactSource/mode/config, not universally no pressure. Descriptor capacity512 and per-address32 are explicit resources; per-address pressure remains UNKNOWN where the typed metric is absent. No arbitrary capacity-proximity cutoff is introduced.

RO traffic is present iff accepted_ro>0. Merge fraction ismerges/acceptedROrequester admissions, undefined when denominator0. It is not a DRAM request saving ratio, a fraction of all ingress requests or a unique-line metric. Final sealed structured records were alreadyselected once per slice; totals do not add repeated kernel cumulative prints. RO live transactions include ready/draining whereas lower-issued-not-returned concurrency is a separate metric.

Wait observations, blocked first-request counts and cumulative request wait sums are not disjoint application critical pathcycles. OrdinaryLineMSHR populations, head/ingress andadmission populations are not mixed into blocked ratios. Issued lowerRO sectors/payloadbytes do not establish completed physical DRAM bandwidth. The schema carries UNKNOWN/null explicitly.

## Finite new-input CPU qualification

SOURCE812_CONV_SCAN_CPU_QUALIFICATION.json records:
- one3.63-second compile of a configuration-only fixture against the eight frozen Source812 libraries, all SHA pinned before andafter; no Core rebuild;
- real productionl2_cache RO constructor andcommandlist binder for both exactinputs andboth policies:4PASS; certified ranges and manifest SHA, complete smallcommandlist SHA, range bounds andcount checked;
- exact old fourconfig sequence plus only the policy flag parsed by the actual Source812 full_option_echo:4PASS,283keys, old282values unchanged;
- no GPU object, epoch, timed request, modelcycle, kernel or Trace body read. It is input-loader/parser qualification, not complete application or timing acceptance.

Original source/ELF/build and broad protocol tests are reused. RemainingMain work is explicit newSource per-input application/mode schema/allowlist, immutableSpec/43fieldHost/22Native+5Host pins, boot/mount and current resource admission. No need to repeat124oldtests or rebuildSource812. Existing acceptedSource78 certificate content is reused; its oldsource qualification isnot inherited.

The two early private script preparation errors (nested NEW_SOURCE5 field and blank option value parsing) were corrected before any application activity. Empty hw_perf_bench_name is retained as an actual effective option, not dropped to manufacture282/283 agreement.

## Proposed next science

Prepare4new starts: Conv3072 Fbaseline/Fpressure andScan Fbaseline/Fpressure, allSource812,850MHz,L100,G32x8,Payload1168/B4/P1/W16/WAD128/TVD128/D512/address32/Line128/FRFCFS128. Allother283options are pinned from their actual old accepted F configurations exceptsourceidentity andaddedpolicy0/1. Eachpoint andfamily releases independently when its ownscientific/resource qualificationpasses; no baseline-completiongate orScanblockingConv.

HistoricalSource78 Fwall: Conv3527.36s, peakRSS1,019,215,872B; Scan31926.96s, peakRSS813,694,976B. These are scheduling anchors, not Source812 guarantees. Conservative finite safetyhardlimits proposed6h/48h with historicalcostas softwarning, RSS3GiB each andAS12GiB/10GiB retained; liveprogress/resources governMain. Both newSource baselines are required; no crossELF performance pairing.

Record activation, native-before-activation, actualRO acceptance, merge, detach/duplicates, completecycles andreal resourcecost. If activation remains0, report that as a useful bounded negative result; do not add pressure thresholds or smallerTag scans without a new exact request. Do not addVector merely to fillbudget.
