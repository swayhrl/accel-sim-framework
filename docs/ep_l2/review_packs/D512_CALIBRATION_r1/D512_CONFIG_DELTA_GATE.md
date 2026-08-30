# D512 runtime-config delta gate

Status: **PASS**

The promoted D512 runtime composite SHA-256 is
`a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416`.
Against the formal D256 semantic base, the normalized effective configuration
changes exactly one authorized field:

```text
descriptor_pool_size: 256 -> 512
```

Unchanged: frequency 850 MHz, Line MSHR 128, descriptor per-line cap 32, WAD
128, L1 BASE (4 banks, MSHR 512, merge cap 8, MissQ 16), Tag/L2 geometry,
payload, bank semantics, lower queues, DRAM timing/scheduler and trace roster.

The D512 Legacy/Banked overlay hashes are respectively
`44d3d3ddcc96b5bee76749ad36540d24c09637b2bf2ddd28e1748be94ec45e15` and
`492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3`.
The fail-closed overlay comparison test
`util/ep_l2/tests/test_d512_config_diff.py` passed after closeout; it requires
exactly this one option difference for both variants. This is configuration
provenance evidence only and does not authorize any new simulator execution.
