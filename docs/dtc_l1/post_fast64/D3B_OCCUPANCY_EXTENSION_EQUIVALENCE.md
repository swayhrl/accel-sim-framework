# D3B occupancy-extension equivalence

Status: `D3B_OCCUPANCY_EXTENSION_EQUIVALENCE_PASS`.

All rows in this document are
`POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`; they do not change frozen FAST64
authority `hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e`.

## Qualified implementation

The extension is Core95 observer commit
`2fcde3eb3fce1502cc0f910cad6f807e530018c5`, rooted through the accepted
Core95 lineage.  It adds only the four time-integrated scalar counters defined
in `LANE_D_OBSERVER_COUNTER_SEMANTICS.md`.  The immutable qualification runner
is SHA-256 `43ad754a87191107fb00f2b9d3ffa1b9183521d38b8ed323aa190c78f138eb24`;
the qualified runtime SHA-256 is
`037d82c61ac90cab41cfdf98234a0889aee16839177a32de23965cb516758d05`.

## Exact off/on gate

The comparison preserves every ordered `DTC_L1_`, `L2_`, `gpu_tot_sim_`, and
`gpgpu_n_` observation.  It requires natural exit status zero, identical
workload/config/trace/runtime/core identity within each pair, equality of all
pre-existing scientific observations, zero of every new field when telemetry
is off, and zero terminal observer identity records when telemetry is on.

| Pair | Pre-existing fields / observations | New fields / observations | Result |
| --- | ---: | ---: | --- |
| NN / IO | 90 / 128 | 12 / 12 | PASS |
| NN / OO | 66 / 104 | 13 / 13 | PASS |
| Btree / IO | 90 / 256 | 12 / 24 | PASS |
| Btree / OO | 66 / 208 | 13 / 26 | PASS |

The retained compact identity, scalar telemetry, and raw-run index are,
respectively, `generated/D3B_OCCUPANCY_EXTENSION_EQUIVALENCE.tsv`,
`generated/D3B_OCCUPANCY_EXTENSION_TELEMETRY.tsv`, and
`generated/D3B_OCCUPANCY_EXTENSION_INDEX.tsv`.  They contain paths and hashes
only; no raw simulator output is committed.

This qualifies the guarded observer for the separately authorized D4 physical
sweep and D5 FAST12 OO diagnostic waves.  It establishes observer isolation,
not a causal interpretation of any future occupancy value.
