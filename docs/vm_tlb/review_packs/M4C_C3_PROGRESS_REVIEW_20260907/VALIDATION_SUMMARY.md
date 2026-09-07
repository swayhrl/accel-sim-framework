# Validation summary

The already committed M4I gates, cold build, fourteen M1–M3 regressions,
eight formal-parser fixtures, behavior-neutral telemetry validation, M4R, and
M4C C0/C1/C2 gates remain the prerequisite evidence.  They are unchanged by
this docs-only snapshot.

The C3 supervisor independently checked every completed arm with:

- simulator exit status `0`;
- exact expected kernel count;
- exactly one `M4C_MEMORY_TELEMETRY_V1` kernel record per completed kernel;
- `summarize_m4c_runs.py --require-level 2`.

At snapshot, those checks had passed for six arms listed as `PASS` in
[FORMAL_ARM_STATUS.tsv](FORMAL_ARM_STATUS.tsv).  They had **not** yet been
run for `prefill-generic` or `prefill-paper` as terminal C3 gates.  C4 export
and offline-locality analysis therefore remained pending.

Telemetry provenance is explicit: runtime counters are either observation-only
simulator counters or existing GPGPU-Sim statistics; immutable-trace locality
is derived offline.  The frozen `L1D_ACCESS_ATTEMPT_WINDOW` interpretation is
documented in [TELEMETRY_CONTRACT.md](TELEMETRY_CONTRACT.md).
