# Track B start override — M4A-C0 rented-host pilot

This file is the current Track-B execution authorization and overrides stale pre-rental wording in older `CODEX_NEXT_STAGE.md` / `M4A_READY_TO_RENT.md` snapshots.

## Authorized now

Execute only:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_C0_RENTED_HOST_PILOT.md`

The user has already rented the Route-E AutoDL host and established SSH reachability from the main development server.

This is a one-round real-host pilot, not the full formal capture Goal.

Codex may use the rented host, install the reviewed locked environment, set `M4A_C_AUTHORIZED=1` only for pilot actions authorized by the stage spec, build/run NVBit, download the frozen Llama model after the cheap gates pass, run real TP4 smoke, collect one `DIAGNOSTIC_PILOT` decode1 trace, copy it back, and perform parser compatibility smoke.

Codex may autonomously diagnose and minimally fix ordinary environment/build/capture-wrapper/runtime issues within the boundaries in the stage spec. It must stop rather than changing frozen hardware/model/TP/workload/NVBit-version/trace-format/research semantics or credentials.

After the pilot, push evidence/report and STOP for ChatGPT review. Do not run formal prefill or formal C2 capture in this round.
