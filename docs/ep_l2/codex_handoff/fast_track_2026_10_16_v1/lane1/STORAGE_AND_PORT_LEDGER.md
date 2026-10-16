# FT Lane 1 data and port ledger V1

Status: IMPLEMENTATION_CANDIDATE_UNDER_TEST. This is a simulator model choice,
not a commercial-hardware claim. Counts below are per slice unless stated.

| Mode | resident / bypass / WB array quota | payload total | banks |
|---|---|---|---|
| OLD_D512_STATIC | 1024 / 128 / no physical WBUF | 1152 | 4 x 288 |
| B16_BANKED | 1024 / 128 / 16 | 1168 | 4 x 292 |
| U_WB16 | same total, dynamically role-owned | 1168 | 4 x 292 |
| B8_BANKED | 1024 / 128 / 8 | 1160 | 4 x 290 |
| U_WB8 | same total, dynamically role-owned | 1160 | 4 x 290 |

All enabled FT modes use the same existing oldest-ready four-bank arbiter:
one arbitrary 128B-line-sized operation per bank/cycle. Resident landing retains
`payload_id % 4 == tag_index % 4`. A sector fill consumes one line-sized bank
operation; no fourth-sector free operation is invented.

Static dirty replacement: one resident source read, one WBUF destination write,
then one WBUF lower-send read. Even when source/destination share a bank the
operations execute on distinct cycles; no implicit dual port. A single shared
128B copy pipeline latch bridges source read and staging write. This latch is
explicitly present in BOTH B and U hardware organizations (idle in U); its
128B/slice, 8KiB/chip cost is outside the tabulated payload-array entry budget
and equal across compared modes. It is not a new freely allocatable pool slot.
No payload data is duplicated into the software packet before the modeled
lower-send read. U_WB transfers the old handle into WB_STAGED without a copy;
it pays the lower-send read using the same banks. copy_lines/copy_bytes and
staging_reads separate these costs. Future copy-cost attribution must be an
explicit representative-point overlay, not free capacity or port service.

WB staging/control lifetime: bounded by the configured payload array and the
128-entry WAD; the lower issue FIFO remains 128 entries at primary settings.
U_WB has no C-entry WB control limit. The transient maps carry one entry per
accepted/issued control object; they are NOT extra data arrays. Additional
metadata per outstanding WB: 11-bit payload pointer, generation, packet binding,
state and age instrumentation. Generation is software unsigned with fail-on-wrap;
no unmeasured physical generation-bit minimum is asserted. A conservative 32-bit
generation implementation plus 11-bit pointer is 43 bits/WB before valid/state.
Allocator free bitmap, bank-class selection and per-slot role/pins need separate
physical implementation estimates; C++ container memory is not a PPA estimate.

## Data transfer to lower memory

Before lower acceptance the authoritative WB bytes reside in the charged
staging payload (or its U_WB original resident slot). The issue-queue packet
carries control/handle only. On the granted staging read the packet obtains its
sector data, then the real memport push transfers data ownership to the bounded
L2-to-DRAM FIFO. Only AFTER push does staging free. WAD remains until set_done.

The model explicitly assumes complete dirty-packet data storage in the existing
lower pipeline. Upper-bound data backing at the unchanged primary capacities:
L2-to-DRAM FIFO 128 x 128B = 16KiB/slice; scheduler 128 x 128B = 16KiB/channel.
Other lower stages retain their configured finite queues/credits, with at most
one live location per transferred packet; a pointer push is not an additional
free copy. These are common lower-pipeline assumptions, accounted separately
from the EP-L2 payload arrays, and not claims that mem_fetch itself is hardware
RAM. Return traffic retains its existing sector/line-sized queue backing.
No new infinite lower data queue is introduced and capacities are unchanged.

Production version labels track four 32B sectors and travel with accepted WB
packets. They check ownership/copy preservation against independently generated
write versions in directed tests; they do not reconstruct numerical values
absent from workload traces. Full-byte requester/atomic validation remains a
separate independent-validation gate, not something cycle equality can prove.

## Forward progress

Every accepted lower read owns a landing before issue. WB lower-send needs only
its existing staging handle, bank service and lower FIFO availability, never a
new resident allocation. Pool-full or same-bank allocation therefore stops new
admissions while older WB can drain and release payloads. WAD completion remains
independent of staging release. Static copy reservations retain victim identity,
WAD and prechecked serialized issue capacity until commit or exact rollback.
There is only one frontend reservation per slice and no second frontend can
steal its issue slots; fill and lower-drain paths do not add issue requests.

LEGACY_SEPARATE_C is not implemented/qualified in this candidate; no WBUF RAM
port count is silently attributed to a user-confirmed hardware fact.
