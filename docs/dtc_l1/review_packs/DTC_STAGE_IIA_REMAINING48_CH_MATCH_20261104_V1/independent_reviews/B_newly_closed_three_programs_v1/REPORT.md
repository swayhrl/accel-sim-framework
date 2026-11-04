# Three newly closed programs: matched six-source evidence

Source-qualified snapshot observed2026-11-04 03:37:20UTC (11:37:20CST), manifest21a10c8a313522b4c7d77b7aaa3c2044e58b5aebaafe4dfdf2ef31529e5fac90. Global context39 accepted/9 awaiting results; this supplement consumes only18 accepted closed sources for3DCONV, histo and stencil. It neither consumes live logs nor relaxes final24's all48terminal gate. No suite or CORE32 GM is inferred from this subset.

## Performance facts

S_CH=CH_P0/CH_F; S_DH=DH_P0/DH_F; R=CH_F/DH_F; I=S_DH/S_CH. All six cells use the same fixed complete registered trace identity per program.

| Program | Kernels/source | CH P0/F128/F256 cycles | DH P0/F128/F256 cycles | S_CH128/256 | S_DH128/256 | R128/256 | I128/256 |
|---|---:|---|---|---|---|---|---|
|3DCONV|254|2958083/2956986/2958542|2200332/2205628/2211632|1.000371/0.999845|0.997599/0.994891|1.340655/1.337719|0.997229/0.995045|
|histo|80|5636037/5551616/5502955|5865589/5789155/5731388|1.015207/1.024184|1.013203/1.023415|0.958968/0.960144|0.998026/0.999250|
|stencil|100|4965921/4965921/4965921|4662889/4662889/4662889|1/1|1/1|1.064988/1.064988|1/1|

3DCONV preserves CH's small F128 improvement(-1097cycles) and F256 regression(+459), plus DH regressions(+5296/+11300). DH still has lower absolute cycles than CH at both F profiles. Histo has a common system benefit for both designs, while CH improves slightly more (I<1), and DH remains slower than CH. Stencil is an exact zero-response control. No per-program best-F selection or blending of original/new source roles occurs.

## Histo: candidate phases localize common benefit

The actual80-launch sequence has prescan/intermediates/main/final repeated20 times. A's fixed144f mapping supplies four disjoint ordinal selectors; all symbols, instructions and trace-member SHAs match current canonical bindings at all six sources. These are source-correspondence phases, not newly certified capture executable or argument values.

| Design/profile | Prescan delta | Descriptor delta | Accumulate delta | Finalize delta | Total delta cycles |
|---|---:|---:|---:|---:|---:|
|CH F128|+1382|-71459|+4556|-18900|-84421|
|CH F256|+701|-105097|+3256|-31942|-133082|
|DH F128|+1111|-68516|+10187|-19216|-76434|
|DH F256|+529|-108339|+3649|-30040|-134201|

Descriptor preparation and finalization provide the net improvements; prescan/accumulate sums regress. Individual negative/zero kernels remain in the detail: CH12854 faster/23 slower/3 equal, CH25656/21/3; DH12854/23/3, DH25655/22/3. A phase benefit does not mean each constituent kernel benefits.

Cumulative DRAM reads(CH P0/128/256)=3373212/3370288/3366832 and DH=3522260/3519236/3514618; write atoms CH=3377460/3377600/3384112, DH=3390592/3392896/3387948. These are32B issued data-command atoms, not distinct bytes or n_req request objects. Read changes are small compared with the reduction in L2 retry events: CH7746461 ->5233160 ->3616006, DH8261985 ->5552097 ->3803978. ICNT-admission block events CH9115166 ->7012252 ->5305446, DH9485267 ->7184020 ->5435175 also decline.

The retry composition changes rather than vanishes. L2 GLOBAL-read MISS_QUEUE_FULL CH7308910 ->4675491 ->1638302, DH7814119 ->4957677 ->1710953. Entry-fail CH3534 ->262652 ->1825854 and DH2661 ->290481 ->1941302 rise. Merge-limit failures are separate (CH21607/23723/27681,DH21196/24715/24102). These are retry event counts, not unique blocked requests, occupancy or critical-path waiting time; no throughput gain from a hypothetical MSHR change is claimed.

Candidate dad09c histo main.cu:128-201 and histo_{prescan,intermediates,main,final}.cu describe range estimation, descriptor streams, shared packed atomics/tails and final reduction/clearing. Source dependencies explain phase order and potential memory paths. The association between fewer retries and improved descriptor/final times does not isolate a causal mechanism. Shared atomics are not automatically normal global cache accesses.

## 3DCONV: stable traffic, worse DH retry composition

All254 actual convolution3D_kernel launches are retained. Neither ordinal nor name is interpreted as the scalar plane argument i. Fixed recovered sourceS dad09c has15 literal terms/11 distinct coordinates and no shared staging or CTA barrier. Corrected/M5/capture-source ancestry remains unresolved; no canonical27-point-stencil or capture-ELF claim is made.

All six sources have2097152 DRAM-read atoms and1901632 write atoms. GLOBAL read-miss sectors2097152 and GLOBAL-write miss sectors2064512 are also invariant. CH accepted GLOBAL sectors15890240 are invariant; DH accepted sectors15089764 ->15090040 ->15090516 rise slightly. Identical totals do not establish identical address sets, residency, request ordering or bank timing.

DH L2 retry events1792366 ->2034446 ->2308236 rise with its cycle regression. Read MISS_QUEUE_FULL drops21979 ->3516 ->3509 while merge-limit failures rise1770362 ->2030831 ->2304628; entry failures25 ->99 ->99 remain a distinct event. DH ICNT-admission events4567514 ->4859740 ->4924028 also rise. CH's corresponding retry totals43568/48187/42372 are merge-limit failures. CH has a slight F128 benefit despite more L2 retries; F256 has a slight regression despite fewer. This rules out equating fewer retry events mechanically with fewer cycles. It does not establish which blocking condition determines the critical path.

Per-kernel variation is mixed: CH128123 faster/110 slower/21 equal, CH256110/124/20; DH12896/158/0, DH25675/179/0. Per-kernel cycles, exact instruction counts and trace SHAs are preserved. All254 print intervals contain issued DRAM reads in the originalP0 sources; intervals are not request-origin attribution. Typed OO service/Tag events and explicit additive differences remain available in the compressed detail; no mean or integral-to-latency conversion is invented.

## Stencil: exact invariance with nonzero but localized reads

All100 actual block2D_hybrid_coarsen_x kernel cycles and all selected additive print intervals are identical within CH and within DH forP0/F128/F256. Each source issues12628 DRAM-read atoms and no DRAM-write atoms. The only nonzero read intervals areK1=8,K2=12616,K44=4. This is not zero whole-replay traffic, and it does not establish cold/compulsory misses or compute-bound behavior. All-access L2 misses73108 comprise12628 GLOBAL reads plus60480 GLOBAL writes; writes must not be counted as read traffic.

L2 retries425(CH)/417(DH), all visible L2 read merge-limit events, and ICNT-admission events242/190 are invariant acrossF. Candidate stencil main.cu:101-148/kernels.cu:12-102 describe ping-pong arrays, x coarsening, register/shared rolling planes and100 repeated launches. The fixed trace sequence is consistent with this source, but no original input-content, scalar iteration ID or capture ELF is newly certified.

## Units, initial state and bank boundaries

All18 sources use the same Core9eed/Framework02775/binary02a28936,1410/1410/1410/850MHz clocks and10MiB L2 layout. F changes FR-FCFS queue64/128/256 with coupled memory-partition shared-credit limit (fixed l2cache.cc:133-149); it is not an isolated queue-only change. CH common PAPER_BASE PIB256 and DH active OO PIB128 remain different structures and costs; generic DHPIB8 is inactive.

All runtime command lists exactly match canonical input contracts. Declared HtoD bytes are134217728(3DCONV),4143520(histo),2097152(stencil); actual commands are retained. perf_sim_memcpy=1,flush_L2=0 invokes forced L2 tag fill without timed DRAM commands. This bounds modeled initial-state interpretation; it does not prove all accesses are warm or all misses are cold. Candidate3DCONV's unspecified B initialization is a source caveat, not newly recovered runtime values.

Final controller/bank diagnostics are recorded separately from additive kernel intervals. Fixed Core dram.cc:555-628 increments bk.n_access only on issued READ-column commands, including L2 allocation reads; WRITE/WB does not increment it. Printed bk?a values therefore measure READ atoms only. Every18x20 controller's16 explicit bank counts reconcile with its read counters, and the full sum reconciles with strict DRAM reads. Banks0..3 have nonzero printed READ atoms; a=0 for4..15 does not prove those banks never write, activate or block.

Whole-replay controller READ-volume CV is identical0.00119604 for all3DCONV sources. Histo CH CV0.106502/0.106770/0.106831 and DH0.107377/0.107758/0.108335 change slightly. Stencil CV0.174639 is invariant. These cumulative-volume measures cannot establish temporal balance, simultaneous bank-level parallelism, bank contention or a scheduling cause. Queue means/maxima retain their original printed diagnostics, are never differenced/summed, and are not exact request lifetime/critical-path latency. Raw latency tokens are diagnostic sampling-window observations; missing does not mean zero.

All cumulative additive differences require explicit endpoints; positive-only missing reasons remain null. Means, gauges and running peaks are excluded from phase sums. Global n_req is a request-object count, distinct from32B read/write command atoms; row-buffer and bank-idle counters are not promoted to explanatory utilization results.

## Evidence and limits

CLOSED_SOURCE_KERNEL_COUNTERS.json.gz contains18 source identities and2604 raw kernel-stat records. ORDERED_KERNEL_SHAPES_AND_CYCLES.json.gz links434 exact kernel ordinals to six-source cycles/instructions/CTA/member-SHA. PRINT_BOUNDARY_COUNTER_ROWS.jsonl.gz supports streaming review. EXACT_PHASE_MAPPING_AND_COUNTERS.json and PHASE_COMPARISONS.json preserve every additive phase endpoint and negative contribution. FINAL_CONTROLLER_READ_QUEUE_DIAGNOSTICS.json.gz keeps final-bank/queue snapshots with the READ-only boundary.

Fixed Atlas47a reports and candidate source copies carry exact path/commit/SHA. A144f selector/trace bindings were matched without changing scientific identity. Original native full-application, input numeric correctness and historical ELF binding remain uncertified; no EP/R2/IR/PQPS result replaces current source identities.

63 raw/source checks +81 derived checks +2791 phase/bank checks=2935 passing CPU/read-only checks. No model/GPU/trace/daemon/control/source/budget/manuscript operation occurred, no live raw was read, and the final24 gate remains unchanged. No new experimental action is implied.
