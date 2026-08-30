# D512 calibration findings (promoted; conservative)

1. **Descriptor blocking is removed, not automatically converted to speed.**
   D256→D512 descriptor-pool full blocks become zero in vectorAdd
   (2,176,663→0), spmv (361,635→0), convolution (3,373,327→0), FWT_7_21
   (1,189,823→0), FWT_11_19 (119,765→0), and scan (60,513,316→0). Their
   D256/D512 cycle ratios are respectively 0.993, 0.995, 0.993, 0.995, 0.999,
   and 0.998: near ties or small slowdowns. Classification:
   `DESCRIPTOR_PRESSURE_LOW_PERF_SENSITIVITY` for the completed D512 change.

2. **Pressure can emerge at Line MSHR and lower path.** D512 raises natural
   Line-MSHR maxima: vectorAdd 92→110, spmv 99→125, convolution 126→128,
   FWT_7_21 102→117, FWT_11_19 96→108, scan 113→128. Convolution develops
   931,416 exact Line-MSHR-full events and scan 19, while their descriptor-pool
   blocks are zero. This is consistent with
   `DESCRIPTOR_THROTTLE_MOVES_DOWNSTREAM`, but it is not proof that a larger
   MSHR would improve performance.

3. **Persistent lower-path pressure explains why descriptor relief alone is
   insufficient.** At D512, L2→DRAM full blocks remain 1,724,003 (vectorAdd),
   288,174 (spmv), 2,455,970 (convolution), 58,792,353 (scan), and 1,077,737
   (FWT_7_21); scheduler-full cycles likewise remain substantial. Native
   application DRAM utilization changes little, e.g. vectorAdd 0.796→0.790,
   spmv 0.666→0.663, convolution 0.651→0.647, scan 0.819→0.817.

4. **No broad new per-address/L1/WAD/payload cause is established.** The
   per-address cap remains 32 and is largely unchanged; spmv's event count
   rises 8,598→20,040, making it an observation for factorial follow-up, not a
   causal claim. L1 and payload/WAD values do not show a new universal D512
   limiting signature.

5. **Temporal behavior is bursty.** In 5K windows, D512 descriptor-average
   peaks are 326 (vectorAdd), 353 (spmv), 321 (convolution), and 399/322
   max/p95 in scan's slice telemetry. See `D512_TEMPORAL.csv`; zero-minimum
   windows rule out a sustained-saturation interpretation.

6. **RO no-MSHR implication.** The data support an MSHR-centric opportunity as
   a hypothesis—descriptor relief exposes naturally higher Line-MSHR
   occupancy/full events and enduring lower-path pressure—but do not justify a
   functional RO decision. The correct current label is
   `INSUFFICIENT_EVIDENCE` for a causal MSHR mechanism claim.

The D512 metadata-cost estimate remains hardware-plausibility context only;
this pack makes no area or performance claim beyond the measured simulator
evidence.
