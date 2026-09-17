# AWMA TLB/PTW characterization — 174-new

Result class: `OPPORTUNITY_PRESENT`.

Scope: `FIXED_WINDOW_PROGRESS_SENSITIVITY`. This study consumes one frozen Q05 Prefill SIM_INPUT and reports bounded-cycle progress sensitivity only. It is not a full-ROI result, hardware calibration, or new mechanism design.

R0 uses source-supported disabled object attribution and disabled segment path. I0 changes only VM mode 2→1. P2 changes only shared L2 TLB ports 1→2. M8 changes only L2 cache MSHR merge 4→8.

Two fresh 10k repeats per D1 profile and two fresh 50k repeats for R0/I0 were completed. Raw logs/telemetry receipts are preserved on node164 at the durable path recorded in `STUDY_MANIFEST.json`.