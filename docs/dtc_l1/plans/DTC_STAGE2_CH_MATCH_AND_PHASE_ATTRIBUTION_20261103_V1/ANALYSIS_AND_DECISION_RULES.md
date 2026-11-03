# CH/DH fairness, stage II scientific decision rules

## Measurement and denominator

For a single *strictly matched* input (i), a downstream F profile (f in \{128,256\}), and cycles (C):

- Downstream benefit within the conventional cache: (S_\mathrm{CH}(f,i)=C_\mathrm{CH,P0}(i)/C_\mathrm{CH,f}(i)).
- Downstream benefit within DTC: (S_\mathrm{DH}(f,i)=C_\mathrm{DH,P0}(i)/C_\mathrm{DH,f}(i)).
- Relative DTC effectiveness under the *same* downstream config: (R(f,i)=C_\mathrm{CH,f}(i)/C_\mathrm{DH,f}(i)). (R>1) means DTC cycles lower.
- Interaction: (I(f,i)=S_\mathrm{DH}(f,i)/S_\mathrm{CH}(f,i)=R(f,i)/R(P0,i)). (I>1) means the new downstream configuration benefits DH proportionally more; it does not alone prove hardware-cost fairness.

For each metric take geometric mean **only on an identical, named intersection** of accepted input digests; report n/35, suite n/total, missing IDs, ties and negative outcomes. Cross-F comparison requires intersection accepted at both F128 and F256, not ratio of 33-member means with distinct populations.

### Stage I authoritative data (2026-11-03T07:11Z)

- (C_\mathrm{CH,P0}) and (C_\mathrm{DH,P0}) strict for 33 programs, baseline CH/DH P0 GM1.096918956 (27 faster, 6 slower); excludes SYRK and lavamd. This is different from older 23-program GM1.123867.
- DH-F128 accepted33 (not SYRK, hybridsort); DH-F256 accepted33 (not SYRK, lavamd); DH F128/F256 joint =32. All factors' original common =31 because scan M16 original is a typed negative.
- DH F256/P0 GM1.022440468 for available33, but GM1.011580804 for all-profile common31. F128/P0 GM1.008258561 common31. F128→F256 GM1.003295032 on same31. These numbers are **DH self-response**, not (I).
- Whole profile F256 is not a universal winner: about 19/33 neutral; convSeparable, scan and hybridsort dominate the positive log-GM. Keep all programs including vectorAdd regression and large-input terminal losses.

## Hardware comparison contract

Fixed: core source, binary, trace+kernel instruction identities, SM64 model, identical DRAM850MHz, L2 10MiB and 40 subpartitions, L2 mapping, clock domains and all input keys. Single difference per F level is FR-FCFS queue plus **shared-credit coupling**. Compare CH and DH L1 organization at matched downstream service. Disclose CH/DH L1 logical Tag/data/PIB/MSHR differences, physical area and frequency unknown. F128/F256 are simulator capacity probes; queue/credit SRAM overhead, critical path, area and energy not yet proven. Hardware area timing require separate RTL/DC release and cost model.

## Prioritization and stopping

1. Keep single-factor F128 and F256 as the two CH matched candidates. They are distinct on resource cost and have small marginal GM, so report both rather than auto-adopt F256.
2. Source reports motivate phase-specific diagnostic questions, not full mechanistic conclusions. Read accepted existing event records before asking for new counters. Instrumentation must preserve telemetry neutrality, exact code identity, and separate explicit future authority.
3. Run evidence-gated candidate pairs only after the original terminal review, CH candidate qualification and source-specific mechanism evidence. The predeclared V2 scheme requires either full35 performance evidence or qualifying fixed suites (≥3 members, GM≥1.01 and positive majority) and **still validates one uniform configuration on all 35**. E384/E768 equality indicates saturation above384; Q64/Q128 population negative argues against indiscriminate missQ expansion. No immediate combo from one large 2DCONV benefit alone.
4. Do not rank a hypothetical large-resource configuration as a physical upper bound. Do not take the best variant separately per input and call it a single hardware design.
5. If full35 cannot be obtained because SYRK/large lavamd failed, submit explicit source/host-resource loss analysis and request **new** engineering/scientific recovery approval separately. No reuse of old UUID, no zero/speedup-one filling, no negative-performance fiction.
6. The official F128/F256 comparison includes negatives and zero gains; the next hypothesis stage may prefer high-impact classes but must retain controls and complete ordinary 35 where feasible.

## Cross-project identity

EP SYRK S/F and lavamd S/F, old downstream18 PQ/PS, and DTC-L2 F128/F256 are different experiment lineages. PQ changes partition FIFO; PS changes DRAM850→1700MHz and clock-dependent timing; EP changes multiple mechanism options and a different binary/core contract. No pooled GM, raw counters or assignment of an EP performance row into DTC missing cells.

## Input and source/trace caveats

Candidate-source correctness issues (e.g. PolyBench ATAX/3MM/GESUMMV potential uninitialized values) and CUDA Samples producer host/ELF discrepancies remain. They are labels on *interpretation*, not evidence that strict simulator replay failed. Workload Atlas V1R1 identifies source facts, but exact original capture ELF and numeric input bytes are not certified. Benchmarks are not automatically end-to-end CPU+GPU measured.
