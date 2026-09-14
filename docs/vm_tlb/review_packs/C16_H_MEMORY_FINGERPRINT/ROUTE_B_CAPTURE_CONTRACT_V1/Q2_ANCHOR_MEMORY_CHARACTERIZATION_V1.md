# Q2 anchor memory characterization V1

These are dynamic address anchors, not phase-wide population claims. Reuse metrics use **OBSERVED_CALLBACK_ORDER**, never hardware global order.

## PREFILL

- LANE_EVENT: 786432
- Access split: `{'READ': 524288, 'WRITE': 262144}`
- Access-width bytes: `{'2': 524288, '4': 262144}`
- Unique VA / 128B lines / 4KiB pages / 2MiB pages: 333952 / 5224 / 164 / 20
- Predicate true / false, executing: 786432 / 0 / 786432
- Callback-order reuse fraction: 0.575358; median distance: 28

Static/MREF event counts:

| static index | MREF ordinal | lane events |
|---:|---:|---:|
| 34 | 0 | 262144 |
| 101 | 0 | 262144 |
| 130 | 0 | 262144 |

Per-launch footprint:

| launch | lane events | unique VA | 128B lines | 4KiB pages | 2MiB pages |
|---:|---:|---:|---:|---:|---:|
| 0 | 786432 | 333952 | 5224 | 164 | 20 |

## DECODE

- LANE_EVENT: 18432
- Access split: `{'READ': 12288, 'WRITE': 6144}`
- Access-width bytes: `{'2': 12288, '4': 6144}`
- Unique VA / 128B lines / 4KiB pages / 2MiB pages: 12291 / 195 / 9 / 7
- Predicate true / false, executing: 18432 / 0 / 18432
- Callback-order reuse fraction: 0.333171; median distance: 1

Static/MREF event counts:

| static index | MREF ordinal | lane events |
|---:|---:|---:|
| 17 | 0 | 6144 |
| 85 | 0 | 6144 |
| 104 | 0 | 6144 |

Per-launch footprint:

| launch | lane events | unique VA | 128B lines | 4KiB pages | 2MiB pages |
|---:|---:|---:|---:|---:|---:|
| 0 | 6144 | 4097 | 65 | 3 | 3 |
| 1 | 6144 | 4097 | 65 | 4 | 3 |
| 2 | 6144 | 4097 | 65 | 3 | 2 |

## Conservative interpretation

For these anchors, Prefill spans 5,224 128B lines and 164 4KiB buckets, while Decode spans 195 and 9. The observed callback-order reuse fractions differ (0.575358 Prefill vs 0.333171 Decode), and their access-width mixes are reported above. These are anchor-local cache/TLB/footprint observations only: they do not establish whole-phase cache, TLB, or reuse behavior before representative coverage closes.
