# TVD state and sector contract — clean/dirty module r1

Source: `56abbacc1192d68995e78561899719649f838079`. Public identity ABI: Lane 1 Core `4fb91f0a5c9eb3bf494a154ea1f24b9a56b34617`, interface publication Framework `cb7d92e4edde97e81520cfdd00762dfe81ee9b20`.

This is a production-linkable metadata module; the old `l2_cache` WAD set is NOT yet replaced. Integration must replace/reuse that address authority rather than instantiate this 128-address table alongside it. Both feature arguments default OFF.

| State | Primary obligation | Read with requested sectors valid | Write/atomic | Reclaim |
|---|---|---|---|---|
| EMPTY | none | miss | normal path | free |
| CLEAN | opportunistic retained payload | extra 1-cycle lookup, real bank service, response enqueue, no promotion | reserve tag/victim resources; promote SAME handle, then normal path | yes if no readers |
| WB_STAGED | mandatory WAD + data awaiting lower accept | retained-data read; exact masks | wait actual WB completion | never |
| WB_INFLIGHT | mandatory WAD + added TVD retention | dirty read-forward | wait actual WB completion | never |
| WB_COMPLETE | opportunistic clean after WB | serve in place | same-handle promotion | yes if no readers |

Clean and dirty directory transitions are verified in this pack. Actual L2-cache producer integration remains NOT_RUN; this is not full TVD.

- Capacity is at most 128 combined WAD/TVD entries. Mandatory WB first reclaims unpinned CLEAN, then WB_COMPLETE; it cannot reclaim STAGED/INFLIGHT. Full mandatory capacity returns refusal.
- `preview_install` is const. Caller first reserves real landing/WB/control/lower resources; `commit_install` verifies revision before any mutation. Failed external reservation invokes no commit. Returned displaced handle remains caller-owned until successful replacement.
- A retained victim must have zero pending sectors; valid/dirty masks are four exact 32B-sector bits. Dirty must be a subset of valid. Duplicate line or duplicate live handle installation is rejected.
- `preview_access` can only return READ_READY at `now > tag_miss_cycle`. Address match alone is insufficient; every requested sector must be valid. Clean partial-sector read miss reclaims directory visibility before ordinary lower service. Dirty missing-sector access waits for true WB completion.
- Clean write/atomic promotes even if the target sector is absent: ordinary resident sector handling then supplies the missing sector. No second authoritative copy or data copy is introduced.
- A move-only read lease pins directory visibility until response enqueue or explicit cancellation; bank denial/ICNT backpressure cannot count a hit or release ownership. Global allocator pin/unpin is still required in the Lane 1 adapter.
- `lower_accept` requires independently accounted lower data ownership. `set_done` is distinct; completion changes retained data to WB_COMPLETE. Pending/inflight data never becomes opportunistic early.
- `epoch_ready` refuses a mandatory WB or live read. Caller must drain and explicitly reclaim each remaining clean payload before teardown.
- 64-bit directory incarnations reject wrap. Hardware generation/age widths remain parameters requiring a lifetime bound; software width is not an area estimate.

## Full-directory dirty promotion

`preview_dirty_promotion` is const and captures the directory revision. After actual external WB/control/lower preparation, `commit_dirty_promotion` transfers the promoted clean payload out and installs the dirty resident victim into exactly the SAME directory slot. Visibility changes in one metadata commit; no 129th address entry and no second authoritative owner is introduced. A stale plan is rejected without mutation. The adapter must implement the matching allocator/tag/packet transaction atomically, using Lane 1's sole resources.

Installation tokens bind both line and writeback class; caller substitution is rejected. Duplicate handle identity across live entries is rejected, including accidental reuse of the displacement candidate's handle. WAD retirement while a reader is pinned changes the entry to WB_COMPLETE but cannot destroy its data. Only the successful response enqueue consumes a read lease; rejected duplicate response/set_done calls do not count completions.
