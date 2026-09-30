# Generic native-oracle harness contract

The harness does not select a target or define an oracle.  After gate binding,
candidate-specific code must provide exactly the gate-defined `B0`, `O1`, and,
only when allowed, `O2` callables.

Required behavior:

1. With feature OFF and diagnostics OFF, execute the gate-bound strong baseline
   without semantic changes.
2. Diagnostics may record receipts but may not alter inputs, outputs, launch,
   ordering, synchronization, or timing boundaries.
3. Candidate code must expose source/build/binary identities, launch/resource
   audit, correctness status, and static SASS sanity evidence before GPU use.
4. The lock wrapper refuses to run unless the immutable gate binding explicitly
   authorizes discovery and identifies a candidate entrypoint.
5. Only `DISCOVERY_TARGET` may run initially.  Validation remains disabled until
   the final Lane 6 contract and preregistered local-headroom gate both pass.
