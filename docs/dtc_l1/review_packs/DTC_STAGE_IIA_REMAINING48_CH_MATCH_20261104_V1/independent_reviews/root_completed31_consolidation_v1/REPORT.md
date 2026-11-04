# Completed31 / fixed CORE32 scientific review: GES pending

Frozen source observation: 2026-11-04T07:02:04.003962+00:00. **46/48 new CH identities accepted;2 awaiting GESUMMV-F128/F256;0 archived simulation negatives;0 verification HOLD.** The exact same31 accepted six-cell inputs are used for both F profiles. All32 frozen identities remain in the table. This is an incomplete completed-subset report, not final32/35/42 coverage, and completion order is not a selection criterion.

All48 one-use science identities were already consumed. Original128 reference slots, first16CH slots and new48 slots retain independent provenance. Six P0 wrappers preserve their underlying accepted identity. No repaired/IR/R2/EP/PQPS source is substituted. Frozen EnglishLaTeXv0.23 and all historical matrices remain unchanged.

## Matched performance

S_CH=CH0/CHF; S_DH=DH0/DHF; R0=CH0/DH0; R=CHF/DHF; I=S_DH/S_CH=R/R0. R>1 describes absolute DH advantage; I>1 describes incremental relative improvement from P0. The Hash family is fixed: these F comparisons concern FR/shared-credit changes and do not newly isolate Hash gains. No program-specific bestF GM is formed.

| F | Same common n/32 | GM S_CH | GM S_DH | GM R0 | GM CH/DH | GM I |
| --- | --- | --- | --- | --- | --- | --- |
| F128 | 31 | 1.013978406 | 1.011876444 | 1.094617971 | 1.092348845 | 0.997927015 |
| F256 | 31 | 1.020571838 | 1.019999506 | 1.094617971 | 1.094004114 | 0.999439204 |

Counts below use exact integer/Fraction signs; rounded1.000000 values do not establish exact zero. A performance regression is retained accepted data, distinct from an archived failed simulation.

| F | Metric | Positive | Exact zero | Regression | Min | Median | Max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F128 | S_CH | 8 | 21 | 2 | 0.951366620 | 1.000000000 | 1.178254428 |
| F128 | S_DH | 6 | 19 | 6 | 0.981742650 | 1.000000000 | 1.187151153 |
| F128 | R | 24 | 0 | 7 | 0.723778820 | 1.023685106 | 3.539772792 |
| F128 | I | 5 | 19 | 7 | 0.913560874 | 1.000000000 | 1.057514975 |
| F256 | S_CH | 6 | 21 | 4 | 0.914653291 | 1.000000000 | 1.370455074 |
| F256 | S_DH | 7 | 19 | 5 | 0.919938023 | 1.000000000 | 1.422263123 |
| F256 | R | 24 | 0 | 7 | 0.693660235 | 1.025241920 | 3.608382469 |
| F256 | I | 6 | 19 | 6 | 0.905203293 | 1.000000000 | 1.112797002 |

## Suite coverage on the same common set

| Suite | Common n | Fixed n | F | GM S_CH | GM S_DH | GM CH/DH | GM I |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CUDA Samples | 9 | 9 | F128 | 1.040091268 | 1.037979388 | 1.018891522 | 0.997969524 |
| CUDA Samples | 9 | 9 | F256 | 1.062320263 | 1.059558829 | 1.018310633 | 0.997400563 |
| Parboil | 7 | 7 | F128 | 1.002158341 | 1.002002379 | 1.022349731 | 0.999844375 |
| Parboil | 7 | 7 | F256 | 1.003419539 | 1.003438934 | 1.022528624 | 1.000019330 |
| PolyBench/GPU | 7 | 8 | F128 | 1.008818884 | 1.002362025 | 1.344464972 | 0.993599585 |
| PolyBench/GPU | 7 | 8 | F256 | 1.009078252 | 1.009929198 | 1.354266614 | 1.000843290 |
| Rodinia | 8 | 8 | F128 | 1.000000000 | 1.000000000 | 1.043820802 | 1.000000000 |
| Rodinia | 8 | 8 | F256 | 1.000000000 | 1.000000000 | 1.043820802 | 1.000000000 |

## DirectF comparison

CH128/CH256 and DH128/DH256 above1 mean F256 is faster. R256/R128 above1 means the same-set absolute DH/CH ratio is larger atF256. All rows use the same31 accepted inputs.

| Metric | n | GM | Positive | Exact zero | Regression | Min | Median | Max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CH_F128_over_CH_F256 | 31 | 1.006502537 | 4 | 21 | 6 | 0.961409904 | 1.000000000 | 1.167480485 |
| DH_F128_over_DH_F256 | 31 | 1.008027721 | 8 | 20 | 3 | 0.901937625 | 1.000000000 | 1.198047207 |
| R_F256_over_R_F128 | 31 | 1.001515330 | 7 | 20 | 4 | 0.937749725 | 1.000000000 | 1.059156683 |

## All32 frozen input identities and source cycles

| Program | Full input SHA | CH0 | CH128 | CH256 | DH0 | DH128 | DH256 | I128 | I256 | BothF complete |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BlackScholes | b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0 | 8993 | 8993 | 8993 | 8971 | 8971 | 8971 | 1.000000000 | 1.000000000 | True |
| convolutionSeparable | 4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449 | 825151 | 702940 | 602100 | 800572 | 674364 | 562886 | 1.011325238 | 1.037803537 | True |
| fastWalshTransform | f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3 | 191732 | 191314 | 191430 | 185317 | 185382 | 185740 | 0.997470011 | 0.996151095 | True |
| histogram | 3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58 | 101432 | 101432 | 101432 | 98202 | 98202 | 98202 | 1.000000000 | 1.000000000 | True |
| mergeSort | dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48 | 114742 | 114742 | 114742 | 111917 | 111917 | 111917 | 1.000000000 | 1.000000000 | True |
| scalarProd | 2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954 | 420477 | 421185 | 422012 | 411009 | 411440 | 409181 | 1.000634498 | 1.008134385 | True |
| scan | 6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39 | 6710840 | 5695578 | 5273582 | 6648993 | 5748280 | 5179817 | 0.981700202 | 1.008719178 | True |
| transpose | 65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc | 241346 | 241346 | 241346 | 237820 | 237820 | 237820 | 1.000000000 | 1.000000000 | True |
| vectorAdd | e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799 | 220803 | 214503 | 223020 | 217305 | 213053 | 236217 | 0.990855823 | 0.929174775 | True |
| bfs | 1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0 | 4330430 | 4330430 | 4330430 | 4170294 | 4170294 | 4170294 | 1.000000000 | 1.000000000 | True |
| cutcp | af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8 | 4502965 | 4502965 | 4502965 | 4490473 | 4490473 | 4490473 | 1.000000000 | 1.000000000 | True |
| histo | 2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64 | 5636037 | 5551616 | 5502955 | 5865589 | 5789155 | 5731388 | 0.998026411 | 0.999249512 | True |
| mri-q | dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4 | 362244 | 362244 | 362244 | 360174 | 359855 | 359855 | 1.000886468 | 1.000886468 | True |
| sad | db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9 | 114310 | 114310 | 114310 | 114870 | 114870 | 114870 | 1.000000000 | 1.000000000 | True |
| sgemm | ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453 | 448633 | 448633 | 448633 | 409417 | 409417 | 409417 | 1.000000000 | 1.000000000 | True |
| stencil | c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266 | 4965921 | 4965921 | 4965921 | 4662889 | 4662889 | 4662889 | 1.000000000 | 1.000000000 | True |
| 2DCONV | d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0 | 1548909 | 1548909 | 1548909 | 462740 | 437573 | 429253 | 1.057514975 | 1.078012268 | True |
| 3DCONV | 79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d | 2958083 | 2956986 | 2958542 | 2200332 | 2205628 | 2211632 | 0.997228912 | 0.995045026 | True |
| 3MM | 977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d | 4191465 | 4191465 | 4191465 | 2402871 | 2402871 | 2402871 | 1.000000000 | 1.000000000 | True |
| ATAX | eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950 | 28428842 | 29882110 | 31081550 | 31880220 | 31894637 | 31321955 | 1.050644367 | 1.112797002 | True |
| BICG | ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef | 26298698 | 24464891 | 24651923 | 28685812 | 29210480 | 28883488 | 0.913560874 | 0.930966524 | True |
| GEMM | fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318 | 1395216 | 1395216 | 1395216 | 826089 | 826089 | 826089 | 1.000000000 | 1.000000000 | True |
| GESUMMV | 769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4 | 114860845 | — | — | 89502220 | 86464623 | 90151547 | — | — | False |
| MVT | f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079 | 26581175 | 25573002 | 24342928 | 34687540 | 35332620 | 35093446 | 0.944507034 | 0.905203293 | True |
| dwt2d | e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008 | 73691 | 73691 | 73691 | 73071 | 73071 | 73071 | 1.000000000 | 1.000000000 | True |
| gaussian | 16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3 | 763932 | 763932 | 763932 | 740717 | 740717 | 740717 | 1.000000000 | 1.000000000 | True |
| heartwall | 731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980 | 8782 | 8782 | 8782 | 8551 | 8551 | 8551 | 1.000000000 | 1.000000000 | True |
| lud | b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8 | 485866 | 485866 | 485866 | 478654 | 478654 | 478654 | 1.000000000 | 1.000000000 | True |
| myocyte | 977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992 | 145909578 | 145909578 | 145909578 | 145147976 | 145147976 | 145147976 | 1.000000000 | 1.000000000 | True |
| particlefilter_float | b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4 | 1861126 | 1861126 | 1861126 | 2100874 | 2100874 | 2100874 | 1.000000000 | 1.000000000 | True |
| particlefilter_naive | 3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e | 511136 | 511136 | 511136 | 384601 | 384601 | 384601 | 1.000000000 | 1.000000000 | True |
| srad_v1 | 0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4 | 8043823 | 8043823 | 8043823 | 7324411 | 7324411 | 7324411 | 1.000000000 | 1.000000000 | True |

## New closed controls and evidence levels

3MM has CH4191465/DH2402871 at all three settings;myocyte has CH145909578/DH145147976;srad has CH8043823/DH7324411. Every actual kernel and selected additive interval has exact zero within-design F response in these inputs. Their absolute CH/DH differences are distinct architecture comparisons under the same Hash family. All earlier positive, zero and negative cases remain included: scalarProd has opposite small CH/DH changes;MRI-Q retains its negativeK3;histo retains negative phases;3DCONV retains both DH regressions;vectorAdd,ATAX,MVT,BICG and particlefilter_float retain their previously reviewed limitations and absolute negatives.

3MM issues zero timed DRAM read/write commands in this prefilled replay. myocyte issues exactly one32B read atom atK1;srad issues13 read atoms inK3/K5/K6. These exposures do not establish compute-bound execution. All-type L2 write misses are not DRAM reads; GLOBAL accepted sectors are32B units; request objects and ICNT blocked-admission events have different meanings. CH common and DH OO counters do not describe equal structures. Missing positive-only reason counters and latency means stay unavailable. Means, gauges and running peaks are not differenced. No live progress preview contributes a cycle, performance ratio, application fraction or ETA.

The myocyte compact6-source evidence contains35958 kernel records.5993=13x461 is arithmetic compatibility with candidate13-RHS logic, not a measured461 solver-attempt count,100ODE steps or full-application certification. Accepted-step/retry IDs and phase_epoch-to-ordinal mappings remain unbound. Its repeated CPU state/parameter HtoD operations require a numerical-coherence boundary: actual simulator hit/new-miss counters do not certify correct reuse of CPU-updated values.

The independent fixed9eed source review binds the effective flush_l1=1,flush_l2=0,prefill=1,invalidate_on_source_event=0 and specific idle invalidation/memcpy callsites. At the reviewed invalidate entry, flag0 takes the ordinary m_L1D invalidation path; the reviewed memcpy path fills L2. This does not exhaust every OO reset path or prove a stale-data bug. Downstream matching alone is not numerical-coherence certification. Candidate source/ELF/y/params binding and runtime OO upload coherence are separate unresolved questions.

3MM candidate source S copies uninitialized E/F/G and uses +=; its binding to historical capture source/ELF/macros and numerical correctness remains unproved. Nominal E=A*B/F=C*D/G=E*F phase labels do not newly certify values. The registered srad502-kernel ROI has seven exact selectors, including distinct450CTA and1CTA reduce phases sharing a symbol. Its extract phase retains a22cycle absolute DH regression. None of these limitations permits repairing or replacing frozen inputs, dropping rows, changing historical acceptance or promoting full-application correctness.

## Hardware, resources and next-step boundary

Core9eedb3131937748f0492fa83aad37d3691118d70,Framework02775fd795cde5aae1480d81cee6eb481d0a08f4,binary02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d,850MHz DRAM and10MiB L2 stay fixed. FR64/128/256 couples to shared credits255/319/447. Across20 controllers F128/F256 add1280/3840 request slots; credits are not another separately counted data buffer.

CH has96KiB ordinary L1/commonPIB256. DH has512 searchable logical Tags,640x128B physical identities,activeOO PIB128 and finite completion service. Its16KiB compatibility cache retains eligible fallback routes.80+16KiB is not a unified effective96KiB cache or equal area. Metadata,ports,wiring,coherence implementation,area,frequency and energy costs remain unquantified. Host RSS/elapsed/storage observations are separate from simulated hardware cost. The public40-point resource snapshot retains its own date; it is not46-point resource coverage.

The recommended next work is conditional: first read-only source/ELF and invalidation-path/coherence qualification; then existing counter/phase attribution; only after full32 evidence and explicit new authorization consider uniform M8xF,Tag/pool/activePIB/finite-service experiments or new observational probes. Any numerical/native GPU validation,new instrumentation or simulation needs its own authorization. No such action starts here.

## Provenance and remaining closure

Root audit `/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/root_independent_cycle_statistics_v1/20261104T071015468833Z/MANIFEST.json`,SHA`60f89782895950134e3946333dbf78dd9fed3d102c131cb5db64435ae80c71bd`,independently rechecks190 accepted RESULT identities,46 new raw terminal-cycle endpoints,exact signs,suite/common/available distributions,directF and effective-option differences. It does not reopen144 inherited raw lifecycles or replace the final full48 archive/recovery audit.

B/C closed supplements:3MM ad4898379cf92922f72026f5b507a9d6e3b47584dc64c9edde756dbfdc71ec4a /4d1b892eea5a3af681f1d26535d9fa77917ddd7cccf3016e923cd8b38d5c0251;myocyte77ba3712318a44e4061997fa564d0f6bcd78196eca04da3c528241616ae82db3 /e060ab9d4e89cadf40b2172a98e0adead5b6c17f72d777475c493b12f211aa64;srad ee24d41079833803fa033c2df67f5475c6e4b7f6c582ab48a8d7c2567e256606 /b035a78eb92ebffcf0620969dfa466d4784f836f3950b2884ed4f2ac294e993f. Packet directories and individual witnesses remain in the Git review package. myocyte invalidation facts72587e571dfde4f1b834f4cce48176205ec1d4e0ce64dd79ea78d26520fa5697 are source facts with explicit scope, not a new model experiment.

GESUMMV-F128/F256 remain missing in this snapshot. The original final CPU waiter still waits for all48 legal terminal outcomes and runs its frozen C/B/Root/render chain once. Final48 lifecycle/true164/native restore audit,final32 statistics/narrative,final48 measured-resource consumption,independent end review,visual approval,immutable final Git/SHA readback and requirement-by-requirement completion audit remain pending. This report does not complete the Goal or release any further experiment.
