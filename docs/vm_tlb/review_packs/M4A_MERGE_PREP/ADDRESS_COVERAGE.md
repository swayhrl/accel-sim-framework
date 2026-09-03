# Exact offline address coverage

Both immutable Route-E rank-0 trace bundles were decoded fully, one predicated
warp lane at a time. This is runtime-range matching against preserved Weight/KV
sidecars, not inferred tensor-lifetime attribution. No GPU was accessed.

| metric | formal prefill | formal decode1 |
| --- | ---: | ---: |
| trace files | 724 | 772 |
| lane references | 2,602,967,364 | 815,478,621 |
| requested bytes | 15,899,995,792 | 4,771,296,188 |
| max observed SimVA | `0x7fddf3808007` | `0x7f81ecb88007` |
| minimum required VA width | 47 | 47 |
| address >= 2^49 / >= 2^56 | 0 / 0 | 0 / 0 |
| list-all / base-stride / base-delta | 0 / 17,920,303 / 65,590,446 | 0 / 3,641,888 / 24,350,141 |
| decoder invariant failures | 0 | 0 |

| ROI / object | references | bytes | 64 KiB pages | 2 MiB pages |
| --- | ---: | ---: | ---: | ---: |
| prefill WEIGHT | 410,255,360 | 6,064,963,584 | 15,443 | 483 |
| prefill KV | 54,935,552 | 158,466,048 | 64 | 3 |
| prefill UNKNOWN | 2,137,776,452 | 9,676,566,160 | 2,433 | 96 |
| decode1 WEIGHT | 63,799,296 | 1,012,989,952 | 15,443 | 483 |
| decode1 KV | 26,136,448 | 195,661,824 | 82 | 4 |
| decode1 UNKNOWN | 725,542,877 | 3,562,644,412 | 119 | 19 |

Class-reference and class-byte sums equal each ROI's lane-reference and
requested-byte totals exactly. `UNKNOWN` is explicit and conservative, not
synthetic KV. Both final outputs were independently aggregated twice from
SHA-bound atomic partials in sorted trace-file order.

External final evidence: prefill SHA256
`6fd209619fae6e348afd109933fe90cf9828d2e65d461b5dc50ccc90d6f4ab5a`
(canonical `6e5daf1e30d5555e9f76059b55a45f4d1f609af573082d7630621c280b6db81b`);
decode1 SHA256
`dc56d89e0e3e6c1f1483fa560fdecf8d4183ac56c15b679911da094a2096c828`
(canonical `60d213c6a057e7099dab0b17bb86faaa1b20519c892ec62f03e9e6e2d3e87858`).
