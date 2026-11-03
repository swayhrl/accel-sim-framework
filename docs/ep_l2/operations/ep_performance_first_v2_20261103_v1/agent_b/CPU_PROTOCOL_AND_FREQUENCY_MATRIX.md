# CPU protocol and frequency matrix

| Scope | Actual result |
|---|---|
| Original78 real104WB frequency reproduction |850/1020/1132 drain;1275/1700 expected original CAM assertion|
| NewSource normal WV,850/1020/1132/1275/1700 |5/5 PASS; highclock12/50 held final-beat intervals; UID/address/payload identity unchanged|
| Two slices in same partition,1275/1700 |2/2 PASS;208 uniqueWB IDs and720 requester completions; HOL23/65 intervals|
| RWQ full / continuous pending arrivals |2/2 PASS;13/13 finite slots, no lost/repeated beat or earlycredit|
| Pinned Victim WB completion |2/2 PASS; pinned landing retained through completion, then lease/pin cancelled and clean drain|
| StaleUID and wrongaddress |4/4 expected original identityguard rejection; actualcredit104->104 and WAD retained|
| ReturnQ backpressure and mixed normal reads/WBs |2/2 PASS;386/537 ReturnQfull observations,368 responses each; full drain|
| Rebased M0T1/M1T1 production RO paths at850/1275/1700 |6/6 PASS: paid lookup, independentLine128 pressure, native-owner exclusion, merge dedup/retry; F additionallylateTag/generation, foursector reversal, foreignpin, epoch/warmup, mixednative128+RO384D512 full/drain|
| Sameaddress newUID / wrongaddress sameUID / oldincarnation / samepayload-ID newgeneration |Actual unchanged TVD component API PASS; stale observation/ticket rejected|
| CPU event golden |WV850/1020/1132 exact signatures and counters unchanged; S850/1275/1700 likewise|

All memory-path checks linked this newCore's eight libraries and matching headers, except explicitly separate old78 reproductions/golden baselines. Test-private access observes real state; malformed negative stimulus deliberately corrupts UID/address in the CPU process. An assert interceptor records guard rejection and credit before/after, then exits86; this override is never linked into the simulator ELF. Invalid input recovery is not claimed.

The queue-full stress uses CPU-only L0 and an80DRAMtick paused core counter to force finite backpressure. ReturnQ stress uses CPU-only ReturnQ4 and DRAM->L2FIFO1, holds cache service, then releases it. Formal candidates retain L100 and all baseline queues. These CPU stresses are not application performance/idealization results.

Engineering fixture failures are retained. The imported dormant helper assumed4MiB was outside its RO certificate, but the actual CPU certificate spans8MiB; native test addresses were corrected to16MiB without changing the certificate. An unsplit128B/foursector request was correctly rejected by the native sector cache; the legal test now submits four32B sector packets. These stimulus corrections changed no production code or protocol assertion. Golden reference event signatures include requester UID/address/cycle and WB slice/cycle/UID/address/payloadID/generation/remainingcredit; equality is boundedCPU evidence, not fullapplicationNI.
