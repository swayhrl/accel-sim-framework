# Simulation consumer preparation report

Status: `174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1`.

The accepted baseline is frozen as
`SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964`
with the exact `NEW_SIM_BASELINE_V1_QUALIFIED /
HASH_BOUND_FIXED_WINDOW_10000` scope. Stale baseline control-plane summaries
were repaired solely from accepted evidence; C12 was not rerun.

Formal consumer admission now requires full hash closure, terminal completeness,
zero drop/overflow, explicit instruction/control semantics, and a real parser
smoke linked to Accel-Sim's authoritative trace parser. All required negative
cases receive no formal ID. The immutable four-record catalog model and exact
10k replay/telemetry wrapper are prepared, and a real historical trace passed
as a parser-only regression fixture.

The first expected producer contract is frozen to the accepted Qwen2.5-0.5B
S2_TEXT Prefill attention launch authority. No current-model trace bytes were
fabricated, no current-model `SIM_INPUT_ID` was issued, no current-model
simulation was run, and C16WARP1/MREF was not converted to traceg. The remaining
dependency is `NODE109_SIM_COMPAT_PRODUCER_BUNDLE`; this stage does not access
or wait for node109.
