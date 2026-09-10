# FAST64 precomputed closeout recovery v2

Status: **RECOVERY COMPLETE FOR THE SEVEN ROWS LISTED BELOW — ALL REMAIN PHYSICAL PRECOMPUTES**

## Scope and safety boundary

Several old-Core immutable rows had already published a natural terminal
receipt, but their original closeout monitor had emitted only its initial
`WAIT_TERMINAL` record.  The raw runs, receipts, original zero-byte lock files,
and original monitor bytes were preserved.  No simulator, runner, config,
payload, or live controller was changed.

The future-only `monitor_fast64_precomputed_row_v2.sh` was invoked with a new
`*_recovered_v2.json` output name for each normal terminal.  It validates the
existing receipt, then runs the existing strict alias-aware validator and
precise failure-signature scan.  These artifacts retain literal historical
Core `bbcbb5e7565417102087bc80b14c349b4e568c05`, runtime
`6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041`, A1
observer, frozen Framework source `037f008b330eb230353b60edf126d6be9f45afdc`,
and their original immutable attempt UUIDs.

## Recovered strict terminals

| workload | mode | attempt UUID | cycles | instructions | compact evidence | result status |
| --- | --- | --- | ---: | ---: | --- | --- |
| 2DConvolution | IO | `7ae2c41b-a4f1-444c-bade-ae93dbc6293e` | 627,590 | 620,347,492 | `generated/fast64_4_precomputed_rows_v1/fast64_4_2DConvolution_io_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| DWT2D | IO | `257ccf84-1651-4116-a36d-b8227a4e1548` | 241,380 | 148,684,429 | `generated/fast64_4_precomputed_rows_v1/fast64_4_dwt2d_io_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| DWT2D | OO | `8d866b57-202e-4386-b221-b1b418d68735` | 234,651 | 148,684,429 | `generated/fast64_4_precomputed_rows_v1/fast64_4_dwt2d_oo_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| Gaussian | IO | `5251ab7f-13b1-43dc-9b7d-0434ef498817` | 3,815,204 | 283,685,120 | `generated/fast64_4_precomputed_rows_v1/fast64_4_gaussian_io_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| Gaussian | OO | `40293c57-f695-42d0-8b70-9bbe6c0842b3` | 3,818,467 | 283,685,120 | `generated/fast64_4_precomputed_rows_v1/fast64_4_gaussian_oo_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| LUD | IO | `ad50c217-c4cc-4cf4-a514-91a368509f03` | 1,089,813 | 184,963,840 | `generated/fast64_4_precomputed_rows_v1/fast64_4_lud_io_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |
| LUD | OO | `ce6a4a2b-8986-4d3d-b8e0-c40f8141f76e` | 1,086,338 | 184,963,840 | `generated/fast64_4_precomputed_rows_v1/fast64_4_lud_oo_cap8192_a1_v3_recovered_v2.json` | strict physical precompute |

Each recovery reports exit `0`, one immutable epoch, clean assertion/fatal/
deadlock/output-mismatch scan, exact mode/config/payload identity, and the
validator's accounting/drain checks.  Observed lower-cap and mode-local queue
pressure counters remain evidence, not failures or performance-selection
criteria.

## Explicit non-promotion

`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` remains the only classification for
these records.  FAST64.3 is still active; FAST64.4 remains physical
precomputation.  No recovered record is a FAST64.4 matrix cell, a speedup
claim, or a mixed-identity triplet.

The two original Hotspot1 old-Core IO/OO terminals are intentionally excluded:
they exited `1` at the already documented source-reachable zero-access
assertion and remain failed/obsolete evidence under
`FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`.  Their authoritative
replacement is the common repaired-Core Hotspot1 triplet, not a collector
reclassification.

## Concurrent repaired-Core work

A new three-window V2 admission audit at
`/tmp/fast64-repaired-ramp4-admission-20260910T105330Z.tsv` authorized two
additional workers: zero sampled swap-out/OOM/PSI/throttling, 22,312,988,672
bytes MemAvailable, 221,153,849,344 bytes cgroup headroom, and 120,192,331,776
bytes output free.  Only one non-duplicative candidate existed: repaired-Core
ATAX/IO was dispatched on CPU 6 as immutable attempt
`9c740af2-0d06-4f8a-b2b1-439128a39fa5`.  It completes the already active
repaired-Core ATAX Base/IO/OO physical-precompute triplet when all three rows
naturally terminate.  No duplicate row was launched merely to occupy the
second admission slot.

After this recovery sweep, Btree/Base naturally exited `0` and the three fresh
repaired-Core Btree rows passed the immutable triplet validator.  Its compact
triplet and Base structural evidence are respectively
`generated/fast64_repaired_ramp_v1/FAST64_BTREE_REPAIRED_CORE_TRIPLET_V1.json`
and `FAST64_3_BTREE_BASE_STRUCTURAL_METRICS_V1.json`.  This is a separate
repaired-Core physical-precompute transition, still pending FAST64.3
acceptance, and is not a retroactive promotion of any recovered bbcbb row.
