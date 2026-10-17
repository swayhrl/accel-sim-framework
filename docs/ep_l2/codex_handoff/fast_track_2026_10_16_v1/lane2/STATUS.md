# Lane2 — EPL2_RTL_COST_OPEN_FLOW_V1, active cost stage

Authority f1980a84c8e637ff2050048bd11b3c1fa5362583, RTL task §4.
T0 2026-10-17T14:55:14Z; first8h checkpoint2026-10-17T22:55:14Z.

Current changed-path hardware source25097f4b6 (full SHA in RECEIPT),
same B16/Unified/S64 full-size parameters. The initial limited suite missed
a same-edge destructive-admission/external-pin race. Actual old-red and
corrected full integration new-green are published under
rtl/ep_l2/validation/pin_admission_r1. No simulator candidate was changed.
B16-map-v3 and UNIFIED-map-v3 were stopped before producing any PPA result.
New B16/Unified ABC-fast mappings use separate central8GiB leases, identical
RTL/library/constraints/effort and512MiB per-job output caps. All retained
EDA outputs remain counted in the central12GiB root. One extra admission
request was correctly refused before execution when shared quota was full.

No EPL2 cell area or STA number is available yet. DC entry/filelist/physical
constraints/library parameters are delivered, DC UNRUN. SRAM146KiB macro
area/delay and reused native Tag/MSHR cost remain UNKNOWN. Serialized
frontend II4 read/II3 write and copy/WB/arbitration/approval differences are
explicit in SIM_RTL_TIMING_GAP; this is not matched-throughput wholeL2.

Old PREP_r1 and old TVD/common/structural evidence remain unchanged.
TVD r14's three uncompiled tests remain NOT_COMPILED_NOT_RUN. No full GPU
application, performance acceptance, Ideal synthesis or background waiter.
Goal continues toward real open reports and first cost revision.
