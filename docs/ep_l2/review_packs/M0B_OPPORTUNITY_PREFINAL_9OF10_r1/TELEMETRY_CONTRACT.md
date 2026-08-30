# Telemetry and configuration contract

Effective configuration hashes:

| Input | SHA-256 |
|---|---|
| core `gpgpusim.config` | `8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3` |
| framework `trace.config` | `19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e` |
| D512 B0 banked base | `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3` |
| M0b ON overlay | `92ce6ea52e0d642c36e08a5c5ac4c44f935456c73600c529f7d4d2944356ab6b` |
| M0b OFF overlay | `5e1ee872b86bde44f1d061a22fb197eaac79056a2240a5b2ba29899743810b39` |

ON is `M0A_ON_M0B_ON_M1_STATIC`; OFF is
`M0A_ON_M0B_OFF_M1_STATIC`.  The intended and checked effective delta is only
`-gpgpu_ep_l2_m0b_stats: 0 -> 1`; M0a stays ON and D512 B0 Banked/static
resources remain unchanged.  M0b does not create bypass traffic.

Line-MSHR identity is `(mshr_address, monotonic_epoch)`.  A newly accepted
tracked allocation advances the epoch, so an address cannot merge separate
incarnations.  Allocation, first-lower-issue, first-fill, and all-required-
sectors-ready are exact source events or directly derived from them.  Last
lower issue, final retirement, and tail intervals are explicitly
`NOT_EMITTED`; measured values are candidate transferable pending-state
lifetimes, never proven avoidable MSHR lifetime.
