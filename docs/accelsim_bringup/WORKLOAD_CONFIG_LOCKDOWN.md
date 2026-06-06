# Workload Config Lockdown

A12 turns A10 row-level evidence into a unique workload/config/run-level lockfile.

The lockfile keeps the strongest evidence row, aggregates source paths, records trace availability, points to the Accel-Sim/GPGPU-Sim config files, and assigns inclusion sets:

- `include_smoke`: smallest P0 readiness set.
- `include_pilot`: bounded expansion set.
- `include_paper_candidate`: high-evidence trace-available rows.

Config equivalence is conservative. `approximate_qv100_sass` means the current Accel-Sim SM7_QV100 trace path can run the workload; it does not prove prior paper config equivalence.

A13 consumes this lockfile directly.
