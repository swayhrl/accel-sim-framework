# M3 PTE request/response conservation

Invariant: every accepted real PTE request is physical and bypasses recursive
translation; it is associated by request ID and expected physical PTE address.
The controller rejects a mismatched response, records a misassociation event,
and records only monotonic issue-to-response intervals.

Evidence at Core `5ba17a1b`:

| Replay | PTE requests/responses | L2-only / DRAM | Misassociation | Final MSHR/PWQ/walkers |
| --- | ---: | ---: | ---: | ---: |
| LUD one kernel, 64KB | 4 / 4 | 0 / 4 | 0 | 0 / 0 / 0 |
| LUD one kernel, 2MB | 4 / 4 | 0 / 4 | 0 | 0 / 0 / 0 |
| BFS, 64KB generic timing | 19 / 19 | 3 / 16 | 0 | 0 / 0 / 0 |

The G3-2 and G3-3 directed suites still pass, including non-recursive request
and hierarchy/PWC checks.  No request loss, duplicate waiter wakeup, or store/
atomic side-effect diagnostic was observed in the replay or directed suites.
