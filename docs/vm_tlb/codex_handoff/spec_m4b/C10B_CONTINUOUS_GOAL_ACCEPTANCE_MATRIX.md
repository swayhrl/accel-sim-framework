# C10-B continuous Goal acceptance matrix

Goal: `C10B_CONTINUOUS_BUILD_RUNTIME_VALIDATION_GOAL`

| Gate | PASS requirement | Goal-mode behavior on failure |
|---|---|---|
| A terminal | `A_TERMINAL_CONFIRMED`; A checkpoint `14edbe200859f6ddf42bc3d459334f184a920a82` valid | hard stop only if A terminal evidence itself is invalid |
| resource gate | 10 s: memory-full <=0.5%, io-full <=1.0%, no swap-in/out, memory/swap/iowait thresholds pass | log, sleep ~5 min, retry; never final `RESOURCE_DEFERRED` |
| shared slot | `/workspace/vm_tlb_post_terminal_heavy_slot.lock` held for every heavy operation | wait/retry |
| C10B-0 | focused compile/tests plus required build/link PASS on repaired architecture-consistent SHA | debug current delta and rerun |
| C10B-1 | accepted standard-mode regression PASS | root-cause/repair; do not proceed knowingly broken |
| C10B-2 | B2–B7 runtime tests PASS, including access class, lifecycle, generation, ordering, fair selector | debug/repair and rerun |
| C10B-3 | runtime telemetry fields, conservation and cross-layer continuity PASS | repair behavior-neutral telemetry or underlying functional bug and rerun |
| C10B-4 | faithful C9 F5 physical PWC implemented/validated, or genuine architecture/model blocker documented | make serious implementation effort; no legacy-PWC relabel |
| C10B-5 | bounded fair-arm runtime sanity PASS | diagnose/repair; results are not performance claims |
| C5 preflight | exact validated runtime identities, commands, provenance, observables and acceptance prepared | continue lightweight prep until complete |
| evidence | `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16` labels preserved | repair report |

Final success:

`C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`

Final hard-stop only:

`C10B_HARD_BLOCKER_WITH_EVIDENCE`

`RESOURCE_DEFERRED` is an intermediate wait state and must never be the final Goal status.