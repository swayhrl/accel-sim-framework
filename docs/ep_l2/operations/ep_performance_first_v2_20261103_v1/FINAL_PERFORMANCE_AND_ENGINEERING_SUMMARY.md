# Performance-First V2: performance and engineering decision

Status: ENGINEERING_COMPLETE / NEW_APPLICATION_STARTS_NOT_AUTHORIZED. Snapshot: 2026-11-04 Asia/Shanghai. Main remains the single science owner. Paper work stays inactive.

## Accepted results reused

The prior retention8/service16 scope finished naturally: 14 starts consumed, 13 accepted, 1 technical failure, 10 high-clock candidates unconsumed/HOLD. All 14 have true164 archives and two independent native restores. Final prior publication: 839f0485d7ead3c2bd62e2734385c1d91688c0d6. The old failure and HOLD allowances are preserved; none finance these new proposals. Four application MS-only NI pairs passed; this does not prove B0/M0a NI.

| Source78 / 850 MHz mode | FWT cycles | GEMM cycles |
|---|---:|---:|
| S |181827|558588|
| W-only |181635|558957|
| CLEAN-only (MS ON/OFF equal)|181441|553632|
| DIRTY-only (MS ON/OFF equal)|179267|570129|
| CLEAN+DIRTY / WV |178951|550642|

WV remains best among these retention modes. FWT prefers dirty service; GEMM has substantial clean Victim service and almost no dirty service. Combined retention still beats either category alone, so neither category is universally removed. Counter marginals are not joint attribution, and retained dirty data at termination is not permanently avoided DRAM traffic.

At 1020 MHz FWT WV=177738 versus 178951 at850: 0.678% fewer cycles. GEMM WV=551783 versus550642: 0.207% more cycles, even though S/WV improves because S slows more. This is not an absolute EP performance win. Stencil remains an accepted strong WV example: S5242939 / WV4768893 =1.09940x.

## Four parallel deliveries

* A: six W/V structural candidates compared. Independent CLEAN-retention-cap Core bf4e48447136b990bd2db15e2972a4394e37d21f, ELF bab27c440a58426b05d4d10312feeaa55cd28319d52e9396009738e036667553. Default128 preserves the Source78 production CPU event trace; finite caps verified with pin/generation/sector/WAD/bank/lower-queue guards. 283 actual options. This optional Source is not accepted, is not the cross-clock repair, and is not included in the two priority budgets.
* B: cross-clock completion-CAM repair Core862376f62ab19f9a677abe31c6a422028b44fcd0, ELF083aa0d72173e8f27b298a76b88898bf117f44d119379b3e3ef9edd1b7ffa52b. Source78 production WB failure reproduced at1275/1700. Existing finite rwq holds the final WB beat until the single Core-domain completion port is available; credit returns after valid completion. No new address lookup/port/queue and no deleted assertion. 17 protocol cases, six new-library RO pairs, default-frequency event golden comparisons and 142 production translation units passed. Shared-queue head-of-line blocking is a real design cost; physical CDC/RTL timing/PPA remains UNKNOWN.
* C: exact 850 MHz Tag-coverage/FR-FCFS single-family and conditional-combination specs; 12 real282 option echoes, production constructor/protocol checks and six mode/profile MS-only CPU NI pairs passed. Full Host102 controls, archive8 and lock6 passed.
* D: 261-point historical/current index separates 248 accepted, 3 unaccepted and10 HOLD; NI OFF duplicates do not enter performance ranking. Read-only resource candidate covers seven scopes, 22 CPU controls passed, foreign promises retained.

Main independently verified344 delivered small-file pins, signed engineering Host/mode reviews, and passed18 full static contracts plus9 reciprocal fair pairs. Main additionally compiled and ran the actual RO loader against the repaired Core and new libraries, with exact Vector4M whole-commandlist certificate and three rejection controls. An initial Host reference-shape mismatch was caught and normalized in Main's receipt, with no Source/ELF/runtime change. No private synthetic accepted rows were adopted as evidence or authority.

## Next two finite family requests

1. SYSTEM_850MHZ_PARAMETER_FAMILY_V2: Source78, FWT/GEMM, S/WV,850 MHz/L100. Initial8 points compare G64W16 and FR-FCFS256 separately; at most4 combo points release per input only after accepted/archive-closed single-family pairs and either both WV absolute cycle reductions >=1%, or one>=3% and the other>=0%. Tag entries256->1024/slice, physical Payload1168 unchanged; FR-FCFS128->256 changes shared credit limit319->447, not private credits or total outstanding cap. Initial estimate ~5.9 host-hours, roughly3h with two free slots; conditional4 ~3 additional host-hours. These are finite modeled resource changes with area/timing unqualified, not equal-area improvements.
2. HIGH_CLOCK_REPAIRED_SOURCE_QUALIFICATION_AND_PERFORMANCE_V1: same new repaired ELF, Vector4M S/F at850 first2, then1275 pair after new850 acceptance/drain/archive; conditional1700 pair only after first4 accepted/archived, CPU1700PASS and max(S850/S1275,F850/F1275)>=1.03. At most6 starts, ~56 reference host-minutes plus qualification/archive; actual newSource cost is not measured. High frequencies are diagnostic service sensitivity, not calibrated GPU hardware. A S-only trigger is not EP success. OldSource78 S1275 cannot be a newSource control, and the old failed cohort is not retried.

See the two exact JSON proposals, all282 options and input identities in main/authorization_packages and main/qualification_review. This is a request for two separate fresh budgets, maximum18 only within these stated ranges, not a global research cap. CLEAN-quota's separate18-point proposal is not requested here.

## Remaining boundary before a model start

Both priority families: user range approval, exact final input/mode eligibility, new scoped sole-entry/native registration and budget, Main global admission/consume and serialized accept/restore integration, fresh resources. New profiles and the repaired Source have no application NI result; B0/M0a NI remains NOT_PROVEN. Zero additional observer-NI points are proposed because no observer is added, with those limits explicitly retained. The repaired Source has zero accepted full applications; new850 S/F is mandatory. Nothing here upgrades CPU fixture cycles to GPU speedup.

Large Trace and archives remain on genuine164. 174 holds builds, small hot outputs and bounded restore work. Resource planning counts actual incremental writes and foreign promises plus ~1GiB emergency, not old35GiB pools or a large reserve per point. Two family carrier windows total256MiB; this is not an extra third reservation. Global two-model limit and serial archive integration are mandatory and not claimed already activated.

Decision: request the two bounded parameter families above; prioritize absolute cycles and prune ratio-only improvements. Keep the independent CLEAN quota as an engineering candidate. No new model, budget or scientific registration was made in V2.

Engineering archive closure: A quota Core/ELF/8libraries archive 846db26ed0652ba55e04767fdf28481e0b4ee937d986c34409b661ef531d678f (11,343,903 bytes) passed two independent native restores of938 members; its413 consumed Framework files match B common recovery. Full historical Framework Git graph/nonbuild docs are not claimed. B repair archive13ea2f5b2ecf8edcef7b45cff30a1cfb35c74251c54ee26c7f60e31bb0a10f89 and Main review archive7cd39309db22f946cf7075ca86221fe721a6587f5a98a2a6eb73115a3429fd40 also have two independent native restores. See each exact archive receipt. No Source candidate has application acceptance merely from these archives.
