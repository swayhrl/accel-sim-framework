# Observer implementation audit

Status: D1/D2 complete; D3 runtime qualification is recorded separately.

## Exact diagnostic Core lineage

| Scope | Accepted parent | Observer commits | Runtime SHA-256 |
| --- | --- | --- | --- |
| Non-2D workloads | `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` | `33266c66943379bda2e61cf78ff0a016bd6ba9ed`, `fb1672518317836ca5cb939d0e671905fe88b94d` | `30d7549e7130ed1a61984428c52c8dc36acd8832f9d0f47a3f78856073e4f801` |
| 2D workloads | `6587238c60214d99491f4048e28ce8a3458c1509` | `df9983d200998a0d7395827f02ba49279e878b67`, `844708a1261a4253f28d08f7db58541a15463844` | `ae78fa8c8a1756c3acaf0d7a037032c8acae43441ff67a072cb1a814d6941d2f` |

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
- matching completion consumes the record and derives allocation-to-ready and
  eviction-to-response durations using the actual response cycle;
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
  completion-before-reaccess negatives, lifetime sums, zero live observer
  records after completion, and disabled controls.

Compiler warnings were pre-existing warning classes in unrelated simulator
sources; neither build produced an observer compilation error.
