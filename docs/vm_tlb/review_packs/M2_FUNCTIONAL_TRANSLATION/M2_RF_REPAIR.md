# M2-RF pending-retry repair

Status: `PASS — STOP FOR CHATGPT REVIEW`
Core: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`
Framework handoff: `e6b8d6b6034acd34f5f5176c3b0f4c3a865c09dc`

## RF1/RF2 behavior

`translation_controller::translate()` first checks the active MSHR for the
same `(ASID, VPN, page size, waiter UID)`.  An already registered waiter
returns `TRANSLATION_PENDING` before either `try_consume_port()` or `probe()`.
A different UID intentionally takes its ordinary first L1/L2 lookup and only
then merges.  `vm_m2_rf_pending_retry_test` asserts one A miss, nine A bypass
retries with no additional L1/L2 accesses/misses/stalls, and B's successful
shared-L2-port lookup/merge in the same cycle.  It also asserts two unique
registrations/wakeups, one release, A's one final completion, and no duplicate
modeled data effect.

## RF3/RF4 counter contract

For future paper-facing TLB miss rate, use `vm_l1_tlb_accesses/misses` and
`vm_l2_tlb_accesses/misses`: after RF1 they count actual probes only and
exclude registered-waiter polling.  Do not use
`vm_translation_lookup_requests` as a miss-rate denominator; it includes
non-pending arbitration attempts, including explicit resource retries.
`vm_translation_pending_waiter_bypasses` exposes the excluded pending retries.

`mshr_allocations` and `mshr_merges` are accepted L2-miss outcomes;
`mshr_full_events`, `pwq_full_events`, and TLB port-stall counters are explicit
backpressure events (not silently dropped requests).  The repair also prints
the configured 64KB page size, MSHR occupancy high-watermark, completed-entry
count, aggregate/max waiter depth, and aggregate/max entry lifetime.  Existing
PWQ wait and walker service counters remain present.

## RF7 fixed-latency sensitivity

| BFS functional mode | latency 5 | latency 50 |
| --- | ---: | ---: |
| walks / completions | 7 / 7 | 7 / 7 |
| L2 probes / misses | 156 / 16 | 156 / 19 |
| new registrations / merges | 16 / 9 | 19 / 12 |
| pending-waiter bypasses | 57 | 901 |
| MSHR lifetime total cycles | 42 | 357 |

The small 16→19 miss difference corresponds to three timing-overlap-induced
new waiter registrations/merges; the L2 probe count remains 156.  The former
same-waiter polling pathology (42→357 misses with only seven walks) is absent.
All runs finish with active MSHR/PWQ/walkers equal to zero.

## RF5/RF6/RF8

The focused boundary test and simulator lifetime proof provide persistence
evidence without adding a flush API.  This pack now includes all standard
files required by `AGENTS.md`.  The provisional G3-1 unit test passes on the
repaired head; G3-1 remains provisional until ChatGPT review accepts M2-RF.
