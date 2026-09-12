# Context-bias audit

18 C14 micro-to-C12 joins were attempted using frozen selector indices. Every result is `CONFOUNDED`: C14 explicitly states `STATE_CONTEXT_NOT_FULL_ROI_EQUIVALENT`, and a kernel-index match does not establish equal binary, telemetry, cache/TLB state, or in-flight queue state. The table reports the numerical contrast without attributing it to cold context. No C15 simulator run was started.

Future contract: capture matched full and cold windows with the same binary/config/trace identity, explicit pre-window warmup, and a state provenance receipt; otherwise retain `CONFOUNDED`.
