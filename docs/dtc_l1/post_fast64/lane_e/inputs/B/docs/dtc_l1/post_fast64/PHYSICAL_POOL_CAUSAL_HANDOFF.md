# Lane B — physical-pool causal handoff

Terminal state: `B_PHYSICAL_CAUSAL_READY`

Evidence class: `EXISTING_DATA_DERIVED_ANALYSIS` plus the source facts in `PHYSICAL_POOL_SOURCE_AUDIT.md`. No new simulator row is used here.

## Accepted input boundary

- Frozen FAST64 authority: `hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02` (`FAST64_COMPLETE_READY_FOR_REVIEW`).
- Stage6 cells input: `docs/dtc_l1/fast64/generated/fast64_6_sensitivity_v3/fast64_6_cells.tsv`, SHA-256 `15dad9c302f2f73194e4ba4ee4ccc76d4e726f5843f57da2e3461532adfbc939`, itself bound by `FAST64_7_INPUT_MANIFEST.tsv`.
- Numeric coverage is 26 strict-terminal physical rows: BICG and GESUMMV at 24/32/40/48 KiB × IO/OO; Btree at 16.5/24/32/40/48 KiB × IO/OO.
- The four BICG/GESUMMV 16.5-KiB entries are retained only in `fast64_6_expected_deadlocks.tsv` as `EXPECTED_RESOURCE_DEADLOCK_NO_NUMERIC_PERFORMANCE`. They are not rows in the raw or normalized numeric tables and are not used in any ratio.
- Btree 16.5 KiB is a distinct strict-terminal numeric row; it is not one of those expected-resource-deadlock boundaries.

Machine-readable outputs:

- `generated/post_fast64/physical_pool_mechanism_raw.tsv` — 26 rows, every compact evidence path and SHA retained.
- `generated/post_fast64/physical_pool_mechanism_normalized.tsv` — raw-counter rate rows plus same-mode 32-KiB performance normalizations.
- `generated/post_fast64/physical_pool_mechanism_normalization_dictionary.tsv` — formula, unit, and provenance for every derived form.

## Descriptive observations, normalized before interpretation

All rates below are events per 1M lower requests unless noted. They establish association only.

| Workload/mode, 24 -> 48 KiB | Performance | Lower traffic | L2 reservation fails | Other bounded facts |
| --- | --- | --- | --- | --- |
| BICG IO | same-mode 32-KiB speedup falls from 1.078 to 0.586; cycles rise 42.35M -> 77.92M | 17.65M -> 17.82M (+1.0%) | 8.092M -> 28.772M | L2 misses 1.429M -> 2.822M; IO duplicate-after-eviction 7,079 -> 20,020; pending hits 9,922 -> 1,073. |
| BICG OO | 1.133 -> 0.911; cycles 37.85M -> 47.09M | 17.64M -> 17.82M (+1.0%) | 9.938M -> 14.721M | OOO retires 1.891M -> 2.238M raw; aggregate reclaim counters are available, but no lifetime is. |
| GESUMMV IO | 1.342 -> 0.713; cycles 78.71M -> 148.26M | 34.22M -> 34.59M (+1.1%) | 3.723M -> 16.747M | L2 misses 1.483M -> 2.646M; IO duplicates 4,347 -> 18,235; pending hits 11,541 -> 1,181. |
| GESUMMV OO | 1.216 -> 0.549; cycles 64.94M -> 143.76M | 34.24M -> 34.60M (+1.1%) | 3.596M -> 16.434M | OOO retires rise 2.771M -> 3.407M raw; aggregate reclaim counters have no duration. |
| Btree IO/OO, 24 -> 48 KiB | 1.000 at every point in each mode | unchanged | unchanged | All listed dynamic counters are unchanged. The IO 16.5-KiB row is slower (0.445 relative speedup) and has 26.6M raw no-free events; IO duplicates remain tiny (1 event at 16.5 KiB, 8 at 24+ KiB). |

The L2-reservation and L2-miss increases above remain after lower-request normalization. Conversely, accepted pending-hit counts decline over these slower BICG/GESUMMV sweeps; they cannot be substituted for pending lifetime. The reported IO minimum-free field is not used in this interpretation because the source aggregation suppresses zero minima (see B0).

## B3 hypothesis adjudication

| Hypothesis | Verdict | Evidence-bounded disposition |
| --- | --- | --- |
| H1 — smaller pools are simply capacity-starved | `DATA_DOES_NOT_SUPPORT` | Source proves a finite physical pool can block a new miss. Btree IO at 16.5 KiB is a measured capacity-pressure correlation (26.6M no-free events and a slowdown, then no-free=0 at 24 KiB). It does not generalize: BICG/GESUMMV show large IO no-free counts at all numeric points, including larger pools that run more slowly, and Btree OO is essentially unchanged at 16.5 KiB. “Simply” is not supported as a cross-workload root cause. |
| H2 — larger pool removes front-end throttling and moves pressure to L2/reservation resources | `DATA_DOES_NOT_SUPPORT` | There is a `MEASURED_CORRELATION` between larger BICG/GESUMMV points and higher L2 reservation failures/misses per lower request. But lower traffic changes only about 1%, IO no-free events do not monotonically disappear, and Btree is invariant. Existing data does not establish a front-end-throttle removal or a causal transfer of pressure. |
| H3 — longer pending lifetime increases pending-Tag eviction and duplicate lower traffic | `INSUFFICIENT_NEEDS_TELEMETRY` | IO source proves the duplicate counter’s necessary event chain: a pending Tag eviction must remain pending and be reallocated before response (`dtc-l1-common.h:213-223,237-249`). Stage6 has no alloc->ready duration and no pending-Tag-eviction count. The available proxies move oppositely in BICG/GESUMMV (pending hits fall while duplicate rate rises), so they must not be called lifetime evidence. |
| H4 — OO reclaim/lifetime changes exposed concurrency | `INSUFFICIENT_NEEDS_TELEMETRY` | The semantic mechanism is `SOURCE_PROVEN`: OO allows any ready entry to retire and protects Tag-invalid physical lines with references until final reclaim (`dtc-l1-common.h:541-603`). Existing OO OOO-retire/reclaim counts correlate with pool point in BICG/GESUMMV, but aggregate counts omit tag-eviction->final-reclaim duration and dynamic occupancy. They cannot quantify the claimed exposed-concurrency arrow. |
| H5 — physical ID/free-list changes downstream mapping | `DATA_DOES_NOT_SUPPORT` / `SOURCE_PROVEN_INERT` | B0 proves `physical_identity.id` is not an input to lower request address, request FIFO priority, L2 set, or L2 partition mapping. Its direct-mapping form is ruled out; only an indirect timing/admission effect remains possible. |

## B4 handoff

H3 and H4 require observer-only information. The exact minimal definitions, event boundaries, and Lane-D equivalence gate are published in `LANE_D_TELEMETRY_REQUIREMENTS_FROM_LANE_B.md`. Lane B has not run B5: no observer-equivalence proof is present in this lane, and no exploratory result is needed to make the bounded classifications above.

## B6 strongest supported chain

| Arrow | Classification | Strongest support and boundary |
| --- | --- | --- |
| physical pool -> admitted/inflight pressure | `SOURCE_PROVEN` | IO/OO source performs a finite free-line search before committing a new miss; no-free returns retryable `NO_FREE_LINE`. This proves the gating mechanism, not a monotonic measured pressure trend. |
| admitted/inflight pressure -> L2 pressure | `MEASURED_CORRELATION` | BICG/GESUMMV larger-pool points correlate with sharply higher L2 reservation fails and misses per lower request, while Btree is invariant. The data has no direct admission/occupancy time series, so it is not a causal proof. |
| L2 pressure -> pending lifetime | `INSUFFICIENT` | Accepted counters contain no alloc->ready latency or equivalent pending-duration exposure. |
| pending lifetime -> pending Tag eviction | `INSUFFICIENT` | Tag-eviction totals do not identify pending victims; pending-hit counts are not lifetime. |
| pending Tag eviction -> duplicate lower traffic (IO) | `SOURCE_PROVEN` | IO source directly increments duplicate-after-eviction only on reallocation while a previously evicted allocation remains pending. |
| pending Tag eviction -> duplicate lower traffic (OO) | `INSUFFICIENT` | Accepted OO has no equivalent duplicate counter, so an IO semantic cannot be projected onto OO. |
| duplicate lower traffic -> performance | `NOT_SUPPORTED` | IO duplicate rates rise in some slowing BICG/GESUMMV points, but Btree’s tiny duplicate changes do not affect performance and L2/miss effects confound the comparison. Existing data establishes no isolated performance effect. |

The scientific conclusion is deliberately plural rather than a forced one: the accepted physical sweep has workload- and mode-dependent non-monotonic performance; direct physical-ID address mapping is excluded; a downstream-L2 association is visible for BICG/GESUMMV; and pending-lifetime/reclaim causal arrows remain bounded pending the minimal observer telemetry.
