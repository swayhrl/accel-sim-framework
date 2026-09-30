# Q1 strong-selection gate

`NONE_RECALL_GATE_FAIL`.

The six preregistered Q1 MULTI_CTA discovery configurations were evaluated on official GloVe-100-angular queries 0..255, `k=10`, using the one frozen device-resident index and original GT top-10. The highest recall was **0.930078125** at `itopk=256, search_width=1`; `itopk=256, width=2` gave **0.929687500**. All six are below the required **0.95**. The source-proven Q1 AUTO/MULTI_CTA 64/1 identity was counted as the 64/1 grid point without duplicating its full run.

No `Q1_STRONG` was selected. Discovery-screen host times are retained only as quality-calibration metadata; they are **not formal latency conclusions**. Do not widen the grid, lower recall, change the stable default build algorithm, or inspect sealed queries 256..511 to manufacture a passing arm.
