# Four-result interim independent scientific review

**PASS for this4/16 interim snapshot only. This is not the final all16 review.** Public authority:11282ee22fa9c1dab56fc4b7b7473b64582e519b; paired scientific snapshot2026-11-04 03:36:12CST. Exactly convolutionSeparable andvectorAdd have both newCH F128/F256 accepted, giving a common2/8 program population. TwelveCH cells remain missing from these statistics. Later running state and watcher timestamp refreshes do not change this fixed denominator.

Fifteen checkgroups pass: each new acceptedRESULT, naturalDONE, source/input/config and strict/raw hashes, five critical source/native-restored members per point, exact original reference SHAs, independent metric/GM recomputation, figure data and13 counter source/excerpt checks. No active raw was read and no model, dispatcher, owner, source, budget or original result was modified.

## Cycles, keeping each design ownP0=1

The following are **normalized cycles (configuration/P0), lower is faster**. The published figure intentionally uses their reciprocals, labeledspeedup(P0/configuration), higher is faster; itsP0 reference is1.

| Program | CH-P0 | CH-F128 | CH-F256 | DH-P0 | DH-F128 | DH-F256 |
|---|---:|---:|---:|---:|---:|---:|
| convolutionSeparable | 1 | 0.851893 | 0.729685 | 1 | 0.842353 | 0.703105 |
| vectorAdd | 1 | 0.971468 | 1.010041 | 1 | 0.980433 | 1.087030 |

| Program | CH-P0 | NewCH-F128 | NewCH-F256 | DH-P0 | DH-F128 | DH-F256 |
|---|---:|---:|---:|---:|---:|---:|
| convolutionSeparable | 825151 | 702940 | 602100 | 800572 | 674364 | 562886 |
| vectorAdd | 220803 | 214503 | 223020 | 217305 | 213053 | 236217 |

Allfour newCH points are strict/archive/native-restore accepted. vectorAddF256 has223020cycles versusCH-P0220803 and is a **performance regression**; it is not an archived failure. Its matchedDH-F256236217 is also a regression fromDH-P0217305. Neither adverse response is removed.

## Same-common-set statistics

Every cell below uses the same two complete inputdigests at bothF levels; no perprogram winner or unequal-denominator comparison. S_CH=CH_P0/CH_F, S_DH=DH_P0/DH_F, R=CH_F/DH_F andI=S_DH/S_CH=R/R_P0.

| F | GM S_CH | GM S_DH | GM R | GM I | Common n |
|---|---:|---:|---:|---:|---:|
| F128 | 1.099242184 | 1.100383430 | 1.024435920 | 1.001038212 | 2/8 |
| F256 | 1.164831162 | 1.143850482 | 1.004940667 | 0.981988222 | 2/8 |

R_P0 GM on these same two inputs is1.023373442. AtF128,I_GM1.001038 is only a nominal0.104% relative proportional increase; atF256,I_GM0.981988 is a1.801% decrease. BothR_GMs remain above1, so the observed two-input absolute ratio slightly favoursDH even thoughF256 improvesCH proportionally more. R>1 andI>1 answer different questions. These two observations do not justify a suitewide conclusion, statistical significance, equal-area claim or configuration adoption.

On this same2-input set F128/F256 cycle-ratioGM is1.059667451 forCH and1.039501733 forDH. Both include thevectorAdd regression. No full8/core32/full35 claim is made.

## Counter semantics: independently supported limits

B_counter_semantics_v1 manifestab54dd7d67e904967e7f32e4f20a00065fcbbf33e4191600cc246f46603b2d51 was byte-verified. Its main audit is33closed sources(32original+firstvectorCH-F128), withconvCH-F256 as a separate34th addendum. C independently checked the four current closed raws, includingconvF128 andvectorF256 beyond that main audit, plus actualbytes and line excerpts for13 source files. This is a focused risk review, not a duplicate broadarchive audit.

The mixed-window conclusion is supported:

- The strict numericdictionary is the final printedblock, but fields have different lifetimes. ForconvCH-F256, lastinterval gpu_sim_cycle=313876 while whole-replay cycles=602100. F128 intervals328720/374220 sum702940; F256 intervals288224/313876 sum602100. These are actual printed simulation intervals, not exclusive mechanism-delay components.
- L2 andDRAM counters persist. ConvCH-F256 finalGLOBAL_ACC_R acceptedsectors=4612044 already contains firstboundary1733668; summing would doublecount. The temporary l2_stats.clear initializes an aggregate, not the liveL2s. Print-boundary differences can be useful, but are not automatically requests originating in exactly that kernel; tails/copies and stream scope matter.
- The500000 sample condition uses currentgpu_sim_cycle, which resets perinterval. Bothconv intervals are below500000 even though their total exceeds it. Cleanup prints beforeupdate_stats folds response sums into num_mfs/mf_total_lat. The secondconvF256 print has averagemflatency112 andavg_icnt2mem_latency5369 with different folded-tail windows; these must not be added as a physical end-to-end decomposition.
- Bothvector raws have positive measured maxima but no targetmean lines. No decimal targetmeans occurred in these four raws; fixedCore prints%lld. Empty strictlatency dictionaries are not zero and do not justify a decimalregex parserfix.
- MRQ numerator/denominator update together atDRAM bankassignment, giving a request-conditioned cumulative queue-age mean when printed. Its timestamp starts atdram_req creation, excluding earlierL2/creditwaiting and laterDRAMservice. It is not totalL2→DRAM time, and requests are not interchangeable with32B dataatoms.
- gpu_stall_dramfull aliases cumulative ICNT→subpartition blockage and can increment for multiple subpartitions perL2tick. It is not isolatedFRFCFS-full time or a disjoint fraction ofGPUcritical cycles. FromvectorCH-F128→F256 it falls5263792→2987121 while cycles worsen214503→223020. Counter decrease alone does not prove faster execution.
- Gauges, runningpeaks, means, retrycounts andSM-cycle integrals retain distinct domains. Terminalzero may mean drained; it is not absent activity. No hit/merge/critical-path causal explanation is promoted from these observations.

The four raw/source spotchecks and exact anchors are inRAW_COUNTER_SPOTCHECKS.json. Existing memcpy-to-L2 preload and cacheflush behavior remain part of interpretation; no real-GPU traffic or complete CPU+GPU timing claim is introduced.

## Figures and remaining boundary

The two currentPNG figures were independently visually inspected and their provider/data hashes verified: plotting source9d996a2784a96a4ab5b970a73ddc5eeb481ab66b538dd3b4558d9e8781ef017e, manifest74ca7aee3521e4437084c44fea4e1de64139d5ab029ad6944b60c09e98b1e7cd. They label4/16, common2/8, retain adversepoints and annotatepending without plottingmissing aszero/one. The actualP0 reference points are valid baselines.

A toolingREADME still calls an older3/n1 example Current snapshot. This is a located documentation staleness, not a scientific-data error: thecurrent provider/data are4/n2. Root will clarify thepublication entry/AS_OF_NOTICE without modifying frozenAfigures. B later refreshedobserved_utc only; this review binds the immutable1936/public11282 snapshot.

Oldoriginal331 and named336 remain separate; allpaired source refs are original-role accepted rows. Six previously ratified P0 no-new-start references forATAX/MVT/BICG remain exact original reference identities, not newly importedIR/R2/EP/PQ/PS variants. OriginalStageI fullcanonical request is unchanged and remaining48 is not released. No48 execution batch is designed here.

**A complete independent review is still required after all16 have terminal evidence, before any next48 execution-batch proposal.** This review does not close that gate, expand authorization, change scientific identity or edit EnglishLaTeXv0.23. Root remains sole publisher.
