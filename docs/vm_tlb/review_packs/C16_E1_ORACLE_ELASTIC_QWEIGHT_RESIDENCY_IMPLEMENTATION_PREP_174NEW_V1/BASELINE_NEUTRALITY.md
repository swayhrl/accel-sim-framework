# Baseline and diagnostics neutrality

Status: PASS.

The CPU-only synthetic cache harness executes 512 ordered accesses and records cycles, instructions, hit/miss/eviction counters, victim and allocation sequence hashes, request-order hash, final output hash and termination.

## Accepted baseline reference vs feature OFF

Both produce functional signature `2447894748496963886` with:

- cycles `5632`;
- instructions `512`;
- hits/misses/evictions `0/512/496`;
- victim hash `5434173523569386371`;
- allocation hash `11341981725595985027`;
- request-order hash `14449080207257068296`;
- output hash `11111217356044830403`;
- termination `PASS`.

The source verifier additionally proves that the accepted `57bb71e...` baseline probe body and data-cache probe/access functions remain the feature-OFF path behind exactly one centralized opt-in branch.

## Diagnostics OFF vs ON

Both produce functional signature `2477205424050287271`, cycles `5632`, instructions `512`, identical victim/allocation/order/output state, occupancy `4`, three denied admissions and 230 protected fills. Diagnostic event collection changes from `0` to `512` without changing functional results.

This is synthetic implementation neutrality evidence, not a real C16 performance result.
