# Exact source index — final RTL candidate

Canonical hardware commit f54d3c054a6a03c85b40a1c5018751958c78a129.
These source locations refer to actual code, not a replacement mechanism plan.

|Path and line|Responsibility|
|---|---|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:127](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L127)|Static fixed resident handle; Unified dynamic map retained|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:154](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L154)|Four full292-slot bank-compatible balanced searches|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:179](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L179)|Finite capacity/admission and generation guards|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:262](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L262)|Preserved same-edge destructive admission/pin exclusion|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:378](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L378)|Physical release at lower acceptance, independent WAD completion|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:417](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L417)|Real16-slot metadata control/data masks|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:435](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L435)|Real charged root/mid/four-word reset tree|
|[rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv:491](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_slice_ctrl.sv#L491)|Group-masked mutable Tag-map data|
|[rtl/ep_l2/rtl/ep_l2_metadata_word.sv:26](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_metadata_word.sv#L26)|Update precedence and local GEN32 step choice|
|[rtl/ep_l2/rtl/ep_l2_metadata_word.sv:30](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_metadata_word.sv#L30)|Exact vector parallel-prefix generation arithmetic|
|[rtl/ep_l2/rtl/ep_l2_metadata_word.sv:78](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_metadata_word.sv#L78)|Bounded lowest eligible index; exhaustive old-scan equivalence|
|[rtl/ep_l2/rtl/ep_l2_metadata_word.sv:99](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_metadata_word.sv#L99)|Charged hierarchical metadata reads; full1168x32 proof|
|[rtl/ep_l2/rtl/ep_l2_metadata_word.sv:127](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_metadata_word.sv#L127)|Actual mapped INV primitive; kept only for real distribution cost|
|[rtl/ep_l2/rtl/ep_l2_payload_sram.sv:7](https://github.com/swayhrl/accel-sim-framework/blob/f54d3c054a6a03c85b40a1c5018751958c78a129/rtl/ep_l2/rtl/ep_l2_payload_sram.sv#L7)|Functional macro model vs synthesis blackbox; no DFF data-array estimate|

Read STRUCTURAL_PROOF, SYNTHESIS_ACCOUNTING, SIM_RTL_TIMING_DELTA and COVERAGE.
All macro/native unknowns and remaining timing/throughput blockers remain explicit.
Formal Core source is unchanged; finite specification remains Core9bd30ed9.
