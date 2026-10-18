# Isolated B preparation — state, ports and cost, before synthesis

Owner redundancy preparation proof R3B_OWNER_PROOF_PREP_v2 is actual word/map
transition preservation under explicit legal event premises, not whole-controller
reachability. Four Tags/eight payloads is an exhaustive symbolic small model.
The written invariant in PORT_AND_STATE generalizes by index symmetry; actual
R2/R3 full controller/late fill/byte regressions remain separate obligations.

Reverse owner removal keeps1024x11 dynamic map and1024 live bits. Add one true
Tag-map read of11bits selected by fill_tag, plus PID equality and live guard.
Remove the payload-owner10bits only after role/live/map equivalence. B16/S64
already have constant owner/map; apply the same forward identity logic fairly.
Unified may remove1168x10=11680 FF; actual mapped cells/area, not a FF count,
determine reported savings. GEN32/role/pins/masks/WAD/address/data stay charged.
Static modes should not be charged a dynamic owner table or a fake RAM.

|Resident field candidate|Required actual reads|Concurrent writes|Consequence|
|---|---|---|---|
|pins6 by Tag|external pin PID lacks Tag; read/response have captured Tag|external pin OR internal read +/- by real mutual exclusion|needs inverse PID→Tag search/storage, or keep pins by payload; cannot delete owner and assume inverse free|
|ready/pending/dirty12 by Tag|req_tag12bits; independent fill_tag pending4bits|one frontend install/write/invalidate plus independent fill ready/pending|at least2 read selections and two independently decoded field writes; same bank P1 does not serialize metadata|
|payload role3 + GEN32|allocation/full-pool eligible, fill/pin/transaction/lower|frontend + lower can coexist|must remain by physical slot for WB/reuse and stale event safety|
|WAD debt|head/active/done/allocation/hazard CAM|allocation,rollback,lower sent,done can coexist under exact priorities|WAD128xGEN32/address/mask/FIFO remains separate real storage|

Moving all resident fields by Tag is therefore not a free1024-word1RW macro.
A partial sector-only12-bit organization could reduce144x12=1728 FF in Unified
while retaining payload pins; it still needs actual mux/decode/write accounting.
No area number is inferred from that bit bound and no macro area is claimed.
Full pin-by-Tag reorganization is STOPPED in this bounded candidate unless its
inverse selection/port implementation is actually provided and qualified. No
new external Tag argument, reduced pin service, serialization or uncharged
storage is silently introduced. The owner-only B candidate keeps payload pins
and all sector state, so it needs no inverse lookup for pin operations.

R3B can be built only after the active A controller discrepancy is resolved;
owner proof alone does not qualify its inherited source. No production PPA is
accepted merely because the abstract owner-invariant proof succeeds.
