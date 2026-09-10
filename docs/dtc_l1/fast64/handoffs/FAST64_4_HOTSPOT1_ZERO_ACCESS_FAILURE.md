# FAST64.4 Hotspot1 zero-access DTC issue

Status: **ACTIVE SOURCE-REACHABLE IMPLEMENTATION REPAIR — NO RESULT PROMOTION**

## Terminal attempts preserved

| mode | immutable namespace | attempt UUID | terminal | classification |
| --- | --- | --- | --- | --- |
| PAPER_IO | `fast64_4_hotspot1_io_cap8192_a1_v3` | `de96e9b8-eea8-4f2f-a179-b0d4b4a7f472` | exit `1`, 2026-09-10T08:40:47Z | `FAILED_SOURCE_REACHABLE_ZERO_ACCESS_ISSUE_ASSERTION` |
| PAPER_OO | `fast64_4_hotspot1_oo_cap8192_a1_v3` | `0fdfa2a2-e9fb-427f-a8dd-97c412172ef8` | exit `1`, 2026-09-10T08:40:50Z | `FAILED_SOURCE_REACHABLE_ZERO_ACCESS_ISSUE_ASSERTION` |

Both namespaces have one immutable-v2 START/TERMINAL receipt chain and retain
their external raw stdout/stderr/resource evidence. Neither is a FAST64.4
result, a parser PASS, or an execution-path-contamination finding. They must
remain in the eventual retry/obsolete map and must never enter an accounting,
speedup, or aggregate table.

## Frozen identity and observed failure

The two attempts use the frozen Hotspot1 trace-list SHA-256
`a731bfc2cbb90b51888e92f3fb188ff4fceb123612a7b1ceb1817bc752e89461`, formal
Core `bbcbb5e7565417102087bc80b14c349b4e568c05`, runtime
`6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041`, A1
observer `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`,
and frozen Framework scientific snapshot `037f008b330eb230353b60edf126d6be9f45afdc`.
The IO and OO config SHA-256 values are respectively
`d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621` and
`546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa`.

Both stderr files report exactly:

`shader.cc:4279: virtual void ldst_unit::issue(register_set&): Assertion 'n_accesses > 0' failed.`

They abort before a valid parser epoch, so no accounting or performance claim
is available. Hotspot1/Base under the same frozen payload and common formal
identity naturally terminated and strictly validated; this isolates the
failure to the PAPER_IO/PAPER_OO issue-side path rather than payload identity
or trace viability.

## Source-backed classification and repair boundary

`ldst_unit::issue()` currently classifies a global/local/param cacheable load
as DTC-cacheable before checking whether its coalesced access queue is empty.
It derives grouped line references from that queue and asserts the resulting
count is positive. `dtc_l1_io_line_references()` iterates that same queue, so
a dynamic load with zero effective accesses reaches the assertion.

The normal memory lifecycle already explicitly treats `inst.accessq_empty()`
as complete in `ldst_unit::memory_cycle()` before DTC PIB admission. Therefore
the source-correct repair candidate is to exclude an empty access queue from
the issue-side DTC-cacheable predicate. For such a no-access instruction it
must preserve zero DTC references, zero pending-write/dependency mutation, and
the existing normal retirement path; it must not weaken the nonempty-reference
assertion or alter DTC allocation/merge/lower semantics.

The active bbcbb simulator processes and their controller/collector bytes are
not modified. Any repair is developed in an isolated Core worktree, requires
focused Hotspot1 IO/OO regression plus an explicit FAST64 result-identity
invalidation/reuse map before formal adoption, and uses fresh namespaces only.

## Next executable action

The isolated Release build with the minimal guard naturally completed the
exact Hotspot1/PAPER_IO payload in
`/workspace/fast64-repair-qual/hotspot1_io_zero_access_guard_r2` (exit `0`,
2026-09-10). It reached `85,206` cycles and `377,291,004` instructions with an
empty stderr/failure scan. The guarded IO lifecycle closes lower
create/issue/response and credit acquire/release at `351,899/351,899/351,899`,
closes dependencies at `353,069/353,069`, and ends with IO PIB/inflight/lower
`0/0/0`. This is an isolated uncommitted repair qualification, not a formal
FAST64 row: its runtime SHA-256 is
`8fc679619587b660bd3a034456f60ed36805af77a15ba499d8083cbc892fd29f` and it
must not be mixed with bbcbb results.

The matching OO qualification remains required before any Core adoption. The
first 2026-09-10 one-worker audit correctly failed closed at
`swap_so_delta=85`, but a later independent 60-second audit passed with
`swap_so_delta=0`, no OOM/PSI/throttle, sufficient cgroup memory headroom, and
124 GiB output free. The exact guarded Hotspot1/PAPER_OO qualification is now
active in the fresh isolated namespace
`/workspace/fast64-repair-qual/hotspot1_oo_zero_access_guard_r0` on CPU 29.
It is uncommitted repair evidence only and must naturally terminate with the
same lifecycle checks before an explicit Core-adoption invalidation/reuse map
is considered. Preserve all bbcbb evidence as mechanism/diagnostic anchors;
do not promote or relabel either original failed attempt.
