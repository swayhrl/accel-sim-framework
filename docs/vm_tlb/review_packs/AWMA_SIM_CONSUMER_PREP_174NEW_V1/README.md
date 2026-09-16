# AWMA simulation consumer preparation on 174-new

Status: `174NEW_SIM_CONSUMER_READY_FOR_INPUT_V1`.

The accepted `NEW_SIM_BASELINE_V1_QUALIFIED` baseline is frozen under the exact
`HASH_BOUND_FIXED_WINDOW_10000` scope as
`SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964`.
Stale baseline summaries are repaired from existing accepted evidence. Formal
admission now uses the authoritative trace parser, fail-closed negative tests
pass, immutable catalog Schemas are prepared, and the bounded replay wrapper
is ready.

No current-model producer bytes were present or fabricated, so no current-model
`SIM_INPUT_ID` exists and no current-model simulation was run. The only
remaining dependency is `NODE109_SIM_COMPAT_PRODUCER_BUNDLE`; this checkpoint
does not access or wait for node109.
