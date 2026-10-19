# A public integration interface, revision 1

Authority: Framework control d9263fa2431592b33e900d9b48c6f20029d8b544,
mechanism_study_2026_10_19_v1. New campaign EPL2_MECHANISM_STUDY_20261019_V1.
Core parent84359d4ba492acb639a2092fa271e9169038bf7d; intended runtime Framework
parent197741be9be9b8e390a557d639503b416d8e95f0; vendor pybind11
f90c430c3a1ce8f08c09942a5a1c3a797bb2295b. The control HEAD is not runtime source.
This first checkpoint freezes integration responsibilities and existing hooks;
it is NOT a compiled or independently qualified simulator release.

## Identity and ownership

Core header `src/gpgpu-sim/ep-l2-mechanism-interface.h` revision1 supplies only
constants, names and an identity envelope. `ep_l2::PayloadHandle` from the
unchanged FT header is `(payload_id, unsigned generation)`. Owner is the full
128B block address. Four32B sector masks and four symbolic producer versions
belong to the actual payload slot; these versions are not numerical SASS bytes.
No module may synthesize a value from an address-only shadow lookup. Generation,
owner, pending/ready sectors and pins must be checked before each use. A Tag
number is not a payload identity, and identity storage is not a second data RAM.

## Fixed resource ledger

| Resource per slice | Budget and existing source |
|---|---|
| resident Tags |1024, native `tag_array` authoritative for sector validity/LRU |
| payloads |1168 total128B, existing `ep_l2_payload_store`; four banks, id%4 |
| S |static1024 resident /128 bypass /16WB; existing128B copy latch retained |
| U |same1168 shared slots, bank-compatible landing; no new victim RAM |
| WAD plus victim directory |128 TOTAL, not128 for each; A owns membership integration |
| line MSHR |128, native `mshr_table` |
| long-lived request descriptors |512 TOTAL; C must reuse this allocator |
| ordinary bank service |one read OR write per physical GPU cycle per bank |
| victim directory lookup |after Tag miss, extra1 physical cycle, at most1/slice/cycle |

Earlier architecture1152/256 numbers are historical, not this campaign's budget.
Runtime geometry/budgets must be checked by E; small directed geometries must be
explicitly labelled and do not replace full-budget production-path tests.

## Current actual hooks and A-owned adaptation points

All paths below are in the exact Core parent, not promises that RO/TVD is ready.

| Operation | Existing source/API and required adaptation |
|---|---|
| preview/prepare | `l2_cache::preview_access`, `ft_access`; previews immutable; reserve all mandatory resources before exposing replacement |
| payload storage | `preview_free`, `reserve`, `transfer`, `release`, `pin/unpin`, `handle_live/handle_owner_matches` |
| native Tag binding | private `tag_payload_handle/set_tag_payload_handle`; A alone changes these and native `tag_array` attach/detach logic |
| requester admission | `descriptor_admitted` inserts exact mf/handle in `m_ft_read_refs` and pins; shared MSHR descriptor pool owns request lifetime |
| lower read | `lower_read_enqueued` records pending sectors on exact handle; no duplicate lower issue for an already merged sector |
| real return | `memory_sub_partition::cache_cycle` calls `ep_l2_payload_fill_request`, then `l2_cache::fill`; reject stale identity before any Tag update |
| response | `ft_response_ready`, `peek_next_access`, `commit_next_access`; retain pins through accepted response enqueue, exactly once |
| rollback | `ft_rollback` cancels service identity, releases staging/landing/quota and WAD reservation, restores old Tag/payload state |
| WB staging | `send_write_request` owns `m_ft_wb`, immutable version snapshot and quota; static copy read/write remain real state transitions |
| lower acceptance | `lower_ready` reads actual staging, `lower_accepted` releases local WB-only data AFTER packet snapshot; not WAD completion |
| WB completion | `memory_sub_partition::set_done` calls `ep_l2_wad_complete`; address order survives the earlier local-data release |
| host prefill | existing `ft_try_force_tag_access` clean/quiescent/pin/sector/generation guards unchanged; physical clock excludes memcpy offset |

B provides a standalone finite directory/lifecycle module, tests and a small
adapter patch for these A-owned hooks. CLEAN_ONLY and dirty-capable versions are
different releases. Clean optional holdings yield slots AND shared directory to
mandatory traffic. WB inflight packets remain immutable snapshots; retaining
local victim data after lower acceptance must retain a real paid slot and new
explicit role, not resurrect a released handle. Pending fill/WB landings cannot
be reclaimed. Do not add independent128-entry victim storage beside WAD.

C provides a standalone eligibility/transaction module, tests and adapter patch.
T=detach pending Tag and M=bypass line-MSHR are independent controls, sharing
512 actual descriptors and actual landing slots. T-only still uses line-MSHR;
M-only retains Tag. Native pool allocation/release changes belong to A. An
unbudgeted address map is not a replacement for the pool. Whole-epoch oracle
must exclude writes/atomics/host updates/alias uncertainty; uncovered requests
fall back. Preserve atomic completion responsibility at the original consumer.

Neither current legacy `feature_tvd`/`feature_ro_pending_state` rejection nor any
other guard is removed by this interface checkpoint. B/C work in their own
modules; A integrates production code once, publishes exact source identity and
lists tested versus unsupported combinations. No whole-branch historical merge.

## First local-diagnostic contract

New independent options (both default0):
`-gpgpu_ep_l2_diag_copy_free`, `-gpgpu_ep_l2_diag_l2_data_free`.
Observer option `-gpgpu_ep_l2_ms_observer`, default0. Options are reserved here;
the initial interface-only checkpoint has not installed them in a runtime.

COPY_FREE supports S only: execute original copy snapshot and target write in
order, retaining placement/capacity/lifecycle, but exempt COPY_READ/COPY_WRITE
from bank grants and their copy-phase delay. LOWER_WB send read remains charged.
L2_DATA_FREE supports S/U: exempt actual L2 payload clients from bank/port
contention and copy-only serialization. It does not bypass cache lookup/misses,
fixed ROP/return latency, queues, response consumption, capacity, same-address
WAD, pins, replacement frontend or lower-memory model. No ALL_DATA/READ_HIT use.
Both diagnostics together, P2/MQ2/RG1/old ideals/quota/S64 and unqualified B/C
combinations are rejected for the first release. Existing non-diagnostic modes
retain their original guard behavior. Newly exempted operations have separate
logical-service counters; they are never labelled real P1 hardware grants.

Residuals: serialized frontend/one active replacement, native Tag/MSHR/
descriptor/WAD bounds, bank-compatible landing capacity, MissQ/LowerQ/ReturnQ/
ResponseQ, fixed query/transfer latency and external memory/ICNT/L1 all remain.
Do not add diagnostic timing differences as non-overlapping program stalls.

## Observations and qualification boundary

UID is `mem_fetch::get_request_uid()`, not a retry counter. Fixed observation
point: after current drains/fills, before frontend admission in
`memory_sub_partition::cache_cycle`. Capture first blocked observation per
request/reason; record first-to-unblock duration separately from attempts and
per-cycle overlapping reasons. Use bounded histogram bins, not access-sized
logs. Occupancy must distinguish real physical roles, visible Tags and pending
landings; missing old fields are UNKNOWN, not0. D's minimum missing fields are
integrated without changing replacement, arbitration or normal simulated cycles.

First finite production qualification must cover default-OFF and observer ON/OFF
cycle equivalence, true cold lower reads/hot hits, real copy data/version and
charged downstream read, same-bank diagnostic intervention, normal P1 clock
0/nonzero memcpy offset, dirty lower-full/WAD lifecycle, same-address write/read,
sector order/late fills/pins and response backpressure. No compile/test PASS is
inherited from the parent for changed source. E grants resources and independently
qualifies exact binaries; E alone launches complete applications within24 starts.

Original174 workspace currently below48GiB; A continues source/control work only.
No lease, compiler, native test, application or permanent waiter is started by
this interface publication. Old R3 DC candidate, old experiments and EN-v17 stay
read-only.
