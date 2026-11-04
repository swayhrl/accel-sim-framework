# Complete32 context for fixed8 structural exploration

The official source-qualified snapshot20261104T105114130127Z_c3570151 now has48/48 newCH accepted and192/192 six-cell slots accepted on one common32-input set. Snapshotmanifest7aa37a91d6506c4de5033cc72f3b0f4233bc43e64e5724128f308423a3809566 and full sourceSHAs are pinned in FULL32_CONTEXT.json. No raw, mechanism report, oldGoal or analysis chain was recomputed/modified.

| Metric/common32 | F128 | F256 |
|---|---:|---:|
|S_CH GM|1.015815817|1.020645454|
|S_DH GM|1.012595183|1.019138263|
|R_P0 GM|1.100072194|1.100072194|
|R GM|1.096584425|1.098447713|
|I GM|0.996829509|0.998523296|

DH own response has7positive/6negative/19zero programs at bothF profiles. CH has9/2/21 atF128 and7/4/21 atF256. DTC relative factorI has5positive/8negative/19zero atF128 and6/7/19 atF256. Larger downstream windows help both designs modestly but do not improve full32 relativeDTC GM above itsP0 value; this does not establish which internal structure is causal.

The fixed8 still cover relevant questions: MVT/ATAX/BICG remain important relative-negative cases,2DCONV/convolutionSeparable cover strong shared downstream sensitivity, andGEMM/vectorAdd/scan provide distinct retention/service/streaming controls. Existing P0 evidence still motivates physical768/1024, coupledOOslots+lowercandidate192 and tagservice2/8 as testable directions. It does not prove these are the dominant bottlenecks across32 or that any new candidate improvesGM. Tag1024/pool640 remains CPUHOLD.

Absolute CH_F/DH_F negative programs (all kept):
- scan: R128=0.990832,R256=1.018102.
- vectorAdd: R128=1.006806,R256=0.944132.
- histo: R128=0.958968,R256=0.960144.
- sad: R128=0.995125,R256=0.995125.
- ATAX: R128=0.936901,R256=0.992325.
- BICG: R128=0.837538,R256=0.853495.
- MVT: R128=0.723779,R256=0.693660.
- particlefilter_float: R128=0.885882,R256=0.885882.

Some negative cases lie outside the authorized8 (for examplehisto/particlefilter_float/sad as applicable above). They are not removed from old32statistics or silently promoted into the new8input experiment. First8 architectural findings will remain8input findings.

GESUMMV is now retained as a complete counterexample to a monotone larger-window story: CHP0/128/256=114860845/106901261/112286106; DHP0/128/256=89502220/86464623/90151547. AtF128 S_CH1.074457,S_DH1.035131,I0.963399; atF256 S_CH1.022930,S_DH0.992797,I0.970543. DH still beatsCH absolutely(R1.236358/1.245526), while itsF256 owncycles regress and relative advantage shrinks. GES is not dropped and itsFR results are not claimed as Tag/physical/PIB/port experiments.

Conclusion boundary: full32 supports searching beyond the FRwindow, not a confirmed attribution to internal DTC capacity. Pool/slot/quota directions retain the original conditional counter predictions, finite-service/initial-state/missingOOpressure/coherence limits and equal-area disclaimer. No existing accepted performance identity or new registration is changed.
