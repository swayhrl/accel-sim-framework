# BICG F128 four-source mechanism review

**PASS_WITH_FORWARD_CLARIFICATION. Consume the original frozenBICG package f2b1dfc69e860b56e96ec70f50490458d843a8808f5f7d598852571790401cba together with forwardtyped/activepath package4550c8e50a7f01578bce24708d5395b674fc6844a578093be1f07c126610eb40.** This is a single-workload mechanism review, not the all16 terminal review or a48-point execution proposal.

Fourteen checkgroups pass. C independently matched fourclosed RESULT/raw/native-exit/source identities, the full ae34174f… inputdigest,145666048instructions/32CTAs/two kernels, exactper-kernel cycles, all33CH/40DH consumed additive counters and20-controller command units. AlloriginalB package members remain byte-exact. Three source roles are originalPhaseI references, including the legally ratifiedP0 aliases; the fourth is newSTAGEII_AUTHORIZED_CH. Nothing is substituted fromIR/R2/EP/PQ/PS variants or rewritten into old331/named336.

## Verified performance facts

| Design/profile | K1 cycles | K2 cycles | Total cycles |
|---|---:|---:|---:|
| CH-P0 |1749396|24549302|26298698|
| CH-F128 |1749396|22715495|24464891|
| DH-P0 |1655347|27030465|28685812|
| DH-F128 |1655347|27555133|29210480|

Within eachdesign,K1 cycles and the consumed additivecounter set are exactly unchanged. CH saves1833807cycles andDH adds524668cycles, entirely in theK2 printed executioninterval. This is phase localization, not proof that every causative request originated inK2; outstandingtails and copies retain their source-window caveats.

S_CH=1.074956680; S_DH=0.982038364; R_P0=0.916784158; R_F128=0.837538137; I=0.913560874. DH has19.3975% more cycles thanCH at matchedF128. These are accepted same-input performance responses; the DH regression is not an archivefailure. They establish neither a suite choice nor a solecause.

The only within-design effectiveoption change isFRFCFS64→128, coupled to sharedcredits255→319. MSHR192perL2subpartition/merge4/missqueue32 and the rest of the model/input remain fixed. The40nominal localMSHR tables are not one global sharedtable. CH/DH retain different L1 mechanisms and no equal-area/cost claim is valid.

## Counter and boundary verification

- CH L2readmisses/DRAMreadatoms fall15513224→14425788, whileDH rises17688864→17956084 despite fewerDHOOfull-line lowerrequests11201149→10620964. AcceptedL2readsectors equal4×thoseDH128Blowerrequests, preserving the32Bsector domain. These facts distinguish upstreamfiltering from downstreammisswork; they do not isolate replacement/order/merging as thecause.
- MISS_QUEUE_FULL attempts fall sharply inboth designs. DH MSHR_ENRTY_FAIL attempts rise142533205→159204818, about99.65% of its final all-L2 reservationfail count. Those are source-defined failedadmission/retry events, not an occupancyhistogram, unique-request count, criticalpath cycles or proof that changing192entries will improve runtime. Repeated attempts can concern the same logicalrequest.
- Reducedmissqueue retries do not mean all limitations disappeared. The fixedqueue/MSHR resources remain enforced. Typedattemptcounts, PIB/Tag state, requestage and executiontime cannot be interchanged or summed as disjoint delays. Printedmeans retain the previously verifiedfold/tail limits; no meandifferencing or end-to-end latencydecomposition was used.
- DH finite-service PIBmean is integral/samples, with samples exactly64×whole-replay cycles; post-ready means use finite-service retiredentries2097152. These are all64SM/event-domain averages, not active-SM-only peaks or criticalpath delay. Lowmeans/terminaldrain do not exclude local PIB/completion pressure.
- DRAMreadatoms are n_rd+n_rd_L2_A; writeatoms are n_write+n_wr_bk. The fixedsource increments ordinarywrites andL2writebacks in mutually exclusive branches, so both writeclasses are includedonce. The four K1 controller snapshots explicitly printzero writes; this is measuredzero, not an omittedfield imputation.

### Late-field check and future consumer rule

Allfour currenttwo-boundary cumulative_additive fieldsets are identical within eachsource:33CH and40DH fields at eachboundary. Everyliteral additivefield appears explicitly in bothrawblocks. The four derivedL2/DRAM fields have explicit bucket/controller ingredients at bothboundaries. Row_Buffer_Locality_write appears onlylater, but is a ratio and is excluded from additive differences. Allcurrent intervaldifferences independently telescope to finaltotals; the currentdata are not affected by analyze_bicg_matched.py's generic prev.get(k,0).

For futureinputs/modes, the safe rule remains stricter: **subtract only explicit same-domain observations at bothboundaries; a missing earlierfield is not zero.** Keep latefields/reasons/means/gauges/peaks unavailable or independently scoped. Constructor initialization can anchor thefirstmodel interval, but does not authorizezero-filling an omitted intermediateprint. No historicalscript or data was rewritten by this review.

## Required active-path and namespace clarification

The original report correctly quoted genericPIB parameter256versus8; these are literalconfiguration values, not the two activePIB capacities. FixedCore source confirms:

- CHmode1 PAPER_BASE enables the commonpaper_frontend. CommonPIB256 admission and the4-bank Tag scheduling limits are active; CH ordinarycache/MSHR service is finite even though DTCfinite_service extensionflag=0. The source invokes try_admit/try_serve_tag on thispath.
- DHmode3 PAPER_OO constructs the commonfrontend asLEGACY/disabled and uses the separateOOfrontend with oo_pib_entries128 for slots/admission. Genericpib_entries8 is not its activeOOcapacity. The genericmshr_entries32 field is likewise not anOO equivalent of CHordinaryL1MSHR512; shader.h applies that override onlytoPAPER_BASE, andOOread bookkeeping is a differentpath.
- The oldDERIVED_DIAGNOSTICS CHrows placed actualCHcommonPIBfull0 andTagconflicts20972288 under OO-prefixed fieldnames. That naming is misleading; do not consume thoseCH values as OO data. Forwardpackage4550 supplies typed CH_common_frontend andDH_PAPER_OO_frontend namespaces. MissingDHOO PIBfull/Tagbankconflict fields staynull, not copiedCHzeros. The underlyingrawcounts and performance facts are unchanged.
- CHTag requestcount represents grantedTagservice attempts, some ofwhich may laterretry cacheaccess; deniedTagarbitration increments conflictcounts separately. Neither field equals unique lowerrequests orDHOOL1 lineprobes. Tagbank serviceconflict and tagmapping eviction are differentevents.

ACTIVE_PATH_SOURCE_CLARIFICATION.json records independentline/SHA anchors inshader.cc,shader.h,dtc-l1-common.h anddram.cc atCore9eedb313. This forwardclarification complements the oldqualified inert-option warning; it does not assert that the oldliteralconfigtable or historicalmeasurements were false, and does not change model/source/input identity.

## Scientific boundary

The B report's leading request/response overlap/filtering/interleaving explanation remains a hypothesis. MoreMSHR retries alone do not prove the criticalcause; fewerTagmappingevictions do not eliminate Tag/PIB/completion bottlenecks; lessMISS_QUEUE_FULL does not release all downstreamlimits. Per-bank occupancytime, requestorder and criticaldependency evidence remain missing. Fixedcandidate source formulas describe K1coalesced/K2row-strided contrast, but capture-source/ELF and numericalbinding remain unresolved. No staticmapping is promoted into a cachehit or MSHRmerge measurement.

Root's separate20-controller balance package was intentionally outside this review's scope; no increased-imbalance claim is made here. All16 must stillclose and receive a complete independentreview before a next48 execution-batch proposal. This review launchesnothing, designsno48batch, changesnoexecutioncomponent/oldhistory, editsnomanuscript and grantsnoadditionalexperiment. Root remains the solepublisher.
