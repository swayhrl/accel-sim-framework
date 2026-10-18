# AD wake state machine

Scope: fixed X2 whole-line PAPER_OO, finite V1; opt-in AD. Structural/timing metadata only. No payload values or ISA consistency theorem.

| Event | Data / broadcast | Consumer dependencies | Identity / Ref | Timing |
|---|---|---|---|---|
| Allocate | `data_ready=false`, original `ready=false` | one pending dependency per distinct held allocation | new physical generation; Ref++ | original allocation/tag limits |
| Pending hit before/within broadcast | still original pending-hit classification while `ready=false` | append slot + slot-generation once, pending++ | same physical generation; Ref++ once | no notification grant on attach |
| Accept sector | no readable flag | unchanged | original request UID/root and physical identity | original response gate; duplicate/wrong address/write reply rejects |
| Accept fourth legal unique 32B sector | `return_cycle` observed; enqueue service return; data still unavailable | unchanged | original physical generation | unchanged `complete()` then `service_cycle+1` |
| Mature original service edge | AD sets `data_ready=true`; `ready` still false | decrement only actually notified consumers | cursor checks live slot generation and held original allocation | shared budget <=4 notifications/SM/cycle; repeated cycle does nothing |
| Notify prefix only | data remains complete | notified consumer may reach own pending=0; unnotified consumer retains pending>0 | all consumers keep Ref until retirement | no borrowed/past quota |
| Late merge before end | data complete but broadcast unfinished | append new waiter with pending++; its own notification still required | new/current slot generation, same physical generation | legal future remaining budget only; same-cycle repeat cannot grant |
| Broadcast end | original `ready=true`; waiters empty | all row notifications delivered exactly once | no automatic Ref decrement | original queue completion edge |
| Hit after end | data/ready true | no new waiter dependency | acquire Ref once | unchanged valid-hit path |
| Candidate/collection | every held allocation data-ready AND own pending=0 AND external=0 | LDST additionally requires all refs admitted and same-warp fence eligibility | no Ref change | original ready->collect +1, collection 4 sectors/cycle, collect-done->WB +1 |
| WB rejected | unchanged | completion ledger/register counts remain live | no Ref decrement/free | original shared operand collector backpressure |
| Successful WB-retire | unchanged | original ledger close and pending-register release | original retirement decrements held Refs | one retirement/SM/cycle |
| K1 source request / tag victim | only lookup visibility removed | consumers/cursor/returns stay live | old physical+generation/Ref retained | original request event, not ordinary delayed tag commit |
| Last Ref of invisible line | line must have finished broadcast | none left | original release/free; later allocation gets new generation | original reclaim accounting |

`physical.ready` remains the X2 broadcast-done flag and determines VALID/PENDING hit statistics. AD does not rename it to mean data return. The new data flag is assigned only inside the original matured `advance_service` stage. The production LDST still calls `complete()` only after the legal whole-line response mask is complete. Calling frontend `complete()` directly is a trusted CPU metadata input, not proof that a payload exists.

Early retire permits processed waiter slots to be reused while later waiters remain. AD discards only the consumed prefix at the service boundary, resets the cursor relative to the surviving suffix, and preserves original physical generation and every surviving slot generation. This avoids retaining dead prefix owners. Assertions check shadow Ref, live unnotified waiter slot identities, exact pending-dependency shadows, data/return prerequisites and waiter bound <= configured OO PIB entries. No assertion was removed.

K1-source-request, ordinary pending-commit, actual kernel-done, and write-after-read visibility without a selected source event remain four different concepts. No ordinary write invalidates a DTC tag through this change. PROXY_FENCE is still an ordering sidecar; it is not a payload coherence mechanism.
