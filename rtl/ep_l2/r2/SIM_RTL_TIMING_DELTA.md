# R2 vs finite SIM vs frozen R1

Specification: finite P1 Core9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f.
R2 deliberately adds no register, stage, queue, free-list state or timing exception.
It changes combinational search/selection, local generation computation and
provably redundant static mapping/owner storage. No SIM source/app rerun.

|Boundary|Finite SIM|R1|R2|
|---|---|---|---|
|frontend read / write II|eligible native frontend once per physical cycle|serialized II4 / II3|same as R1|
|static dirty copy|source reservation/read and later copy+incoming on independent banks possible same physical cycle|source read / sync return / staging write / incoming commit serialized|same as R1|
|response return|existing simulator queue/model|one real held1024-bit response; read pin until consume|same as R1|
|WB return|symbolic granted data capture|SRAM return -> shared copy latch -> held WB register|same as R1|
|bank arbitration|oldest ready vector/arrival|three-client per-bank round-robin, P1, independent banks concurrent|same as R1|
|dynamic landing|lowest compatible eligible PID|full-capacity ascending priority|balanced four-bank priority; identical PID and cycle|
|WAD first-free|bounded128, old-address hazard|address CAM + serial first-free|same CAM, balanced first-free; identical entry/cycle|
|SRAM read|simulator array access model|assumed1-cycle 1RW;4x292x1024,128byte enables|same as R1; real macro delay/area UNKNOWN|
|native approval|C++ precheck and saved symbolic rollback|held native_ready required before destructive write|same as R1|
|WAD set_done|after lower_accept; generation qualified|separate acceptance frees local slot, done frees WAD|same as R1|
|generation|bounded identity contract|GEN32 saturating admission, GEN3 exhaustion test|same widths/steps/priority; local increment|

No matching SIM-performance cost pairing. If remaining worst paths require
pipelining, only a separate Lane1 proposal is authorized; no pipeline silently
introduced here. SRAM macro/Tag/MSHR/interconnect costs and physical closure
remain separate outstanding work. No whole-slice PPA claim.
