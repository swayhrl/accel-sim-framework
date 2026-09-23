# AWMA RTX4080 simulator baseline V1

Decision: `AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`.

`AWMA_RTX4080_SIM_BASELINE_V1` is defined by:

- hardware platform `RTX4080_ADA_ACCELSIM_BASE_V1`, config `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`;
- frozen model-relative 10/80 VM overlay (not RTX4080 hardware latency);
- V1 frontend via `GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1` and `GPGPUSIM_READY_APPLICATION_V2=0`;
- Legacy retained as a selectable control;
- 0/80 retained as diagnostic companion;
- V2R1 retained as diagnostic-only and excluded from the baseline;
- Segment F0 dormant.

The source default is unchanged. Consumers activate the named manifest and `baseline.env`.
