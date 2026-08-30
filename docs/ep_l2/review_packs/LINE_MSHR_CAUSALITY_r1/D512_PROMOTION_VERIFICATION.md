# D512 descendant promotion verification

Lane B has established `D512_PREFLIGHT_PASS`, `D512_READY`, and
`D512_MIRROR_COMPLETE` for:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
D512 runtime composite SHA-256
a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

The Lane-E D512/M128 equivalence, D512/M256 convolution, and D512/M256 spmv
manifests each record the exact Core and Framework parent; the M128 overlay
SHA-256 is `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3`.
The two MSHR256 overlays differ from their matching D256/D512 MSHR128 overlays
only in `dl2 A:128:1 -> A:256:1`, as rechecked by the Lane-E config-diff test.
All required trace identities, 850 MHz setting, descriptor=512, per-address
cap=32, and terminal/parser invariants match the accepted candidate contract.

Result: exact matching D512-derived Lane-E rows are promoted from
`SPECULATIVE_PENDING_GATE` to `PROMOTED_VALID_CALIBRATION` without rerun.
