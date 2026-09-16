# AWMA 174-new LDGDEPBAR consumer-validator hotfix

Status: `174NEW_SIM_CONSUMER_LDGDEPBAR_VALIDATOR_HOTFIX_PASS`.

## Claim

The strict consumer validator now treats exact base opcode `LDGDEPBAR` as an addressless control opcode. `LDGDEPBAR width=0` with no address passes; address-bearing `LDG.E.32` and `LDGSTS` with width zero still fail.

## Authority

- Coordination authority: `67c9f916dfc7211ed2d931ff4cd1cf0c5bdd889b`.
- Accepted consumer base retained: `25aa29862239a408099639ae9d5f1a0ea4fee1e1`.
- Producer checkpoint reviewed, not modified: `e46193b94dd969a988126fc9fa5545da08b26d18`.

## Boundaries

- No producer data, Q05 workload/target, or simulator binary was modified.
- Frozen `gpu-simulator/trace-parser/trace_parser.cc` is compiled as the authoritative parser and is unchanged.
- `SIM_BASELINE_ID` is unchanged; this patch creates no `SIM_INPUT_ID`.
- No simulation replay or 10k current-model run was performed.
- Mode-2 base-delta remains an excluded frozen-baseline boundary; this hotfix does not alter it.
- This is a false-positive validator classification correction, not a relaxation of address-bearing memory requirements.