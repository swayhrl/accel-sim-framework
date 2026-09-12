# Observer implementation audit

Status: D1/D2 complete; D3 runtime qualification passed and is recorded in
`OBSERVER_EQUIVALENCE_REPORT.md`.

## Exact diagnostic Core lineage

| Scope | Accepted parent | Observer commits | Runtime SHA-256 |
| --- | --- | --- | --- |
| Non-2D workloads | `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` | `33266c66943379bda2e61cf78ff0a016bd6ba9ed`, `fb1672518317836ca5cb939d0e671905fe88b94d`, `f2c28217be36c9756afab3d937d6aaf35f23cd7b` | `a7aeace93c288deb2c4f79a0a19c84ce2553744ef4297a2f64aedf38db9ae411` |
| 2D workloads | `6587238c60214d99491f4048e28ce8a3458c1509` | `df9983d200998a0d7395827f02ba49279e878b67`, `844708a1261a4253f28d08f7db58541a15463844`, `7e109d17799f18a9f07de5f63577719d670860cb` | `74667d729f60fcd6f5b77c08169764ba2b61585fb43bf77576f0613657ea99dd` |

Both Core branches are independently rooted at their accepted parent. No
accepted Core or FAST64 runtime was modified.

## Source-isolation finding

`-gpgpu_dtc_l1_post_fast64_telemetry` is an unsigned parser option with
default `0`. Its value is transferred once into DTC configuration. With the
option disabled, the observer maps/counters are never populated and all new
printed fields remain zero.

The changes are observation-only:

- frontends record a successful allocation by `(physical id, generation)`;
- a pending Tag eviction records its event cycle;
- matching completion consumes the allocation record and derives
  allocation-to-ready duration; IO additionally derives eviction-to-response
  duration using the actual response cycle;
- an OO Tag-invalid line with a live reference records its eviction cycle and
  derives deferred-eviction-to-final-reclaim duration only at that exact
  generation's final reference reclaim;
- OO adds the source-matched duplicate-after-eviction counter, incrementing
  only after a replacement allocation is guaranteed to be `NEW_MISS`.

No observer field is read in Tag lookup, victim selection, allocation/free
choice, retirement/reclaim, lower scheduling, or normal completion routing.
Observer metadata is keyed by the same generation identity already used for
completion validation, so a recycled physical slot cannot be attributed to an
old allocation.

## D2 regression record

For both Core descendants:

- a clean isolated Release `gpgpusim` build passed;
- `dtc_l1_m1_common_test`, `dtc_l1_bad_generation_test`, and
  `dtc_l1_completion_accounting_test` all passed;
- directed tests cover IO and OO pending-eviction/re-access positives,
  completion-before-reaccess negatives, IO response and OO final-reclaim
  lifetime sums, immediate-reclaim exclusion, zero live observer records
  after drain, and disabled controls.

Compiler warnings were pre-existing warning classes in unrelated simulator
sources; neither build produced an observer compilation error.

## D3 qualification record

NN and Btree each passed telemetry-off/on exact compact-stat equivalence in
both IO and OO modes on the Core95 observer descendant. The comparison retains
ordered compact-stat blocks (two for Btree), requires exact equality of
pre-existing accounting, and checks terminal observer drain. The complete
provenance manifest, retained telemetry values, and excluded-attempt ledger
are linked by `OBSERVER_EQUIVALENCE_REPORT.md`.

## D3B occupancy-extension qualification record

The reviewed occupancy-only extension is separately qualified on Core95
commit `2fcde3eb3fce1502cc0f910cad6f807e530018c5` with runtime SHA-256
`037d82c61ac90cab41cfdf98234a0889aee16839177a32de23965cb516758d05`.
NN and Btree each pass exact telemetry-off/on comparison in IO and OO.  The
comparator checks the complete ordered scientific-stat sequence, including
both Btree blocks; all 90 IO and 66 OO pre-existing field families match
exactly, new fields are zero off, and terminal identity records are zero on.
The D3B retained compact evidence is in
`generated/D3B_OCCUPANCY_EXTENSION_EQUIVALENCE.tsv` and
`generated/D3B_OCCUPANCY_EXTENSION_TELEMETRY.tsv`.
