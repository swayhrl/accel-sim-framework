# M4A-C Goal-mode admission report

Stage: `M4A_C_FORMAL_CAPTURE`

## GOAL_BLOCKED

G0 rejected formal-capture activation. The immediately preceding pilot report
closed with `PILOT_BLOCKED`, rather than the exact required
`PILOT_PASS_READY_FOR_GOAL_CAPTURE`. The recorded blocker is absence of a
remote Hugging Face credential authorized for
`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.

No Goal capture action was taken: no `M4A_C_AUTHORIZED=1`, model download,
TP4 Llama execution, formal prefill/decode1 trace, parser/simulator run, or
remote reclamation occurred. The rented instance remains intact and idle.

Minimal user action: safely provision a valid authorized `HF_TOKEN` in the
remote runtime session, then issue a new handoff to resolve/rerun P5. Goal mode
cannot bypass its own pilot admission condition.

The G0 decision, source anchors, and links to the preserved pilot evidence are
in `docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/`.
