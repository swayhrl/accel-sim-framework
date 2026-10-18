# R3 port/state contract — bounded source-derived restructuring

Authority1e56ba6e; frozen R2 hardware f54d3c054 / publication1b011c6a5.
Full1024Tags/1168payload/128WAD/GEN32/four292-row banks/P1 retained.
R1/R2 worktrees, sources, accepted raw/results and tests are read-only.

## Source events and precedence (not an assumed single writer)

|Event|Enable/state|GEN target/step|Other independently writable fields|
|---|---|---|---|
|reservation|req_fire,IDLE,install U(new/dirty) or static dirty|one free landing/staging,+1|role,owner; WAD allocate GEN+1/address/mask|
|install|native_commit,COMMIT,op0,!new_reserved|p_landing,+1 or old_live+2|resident role/owner/sector masks; dirty victim becomes WB|
|invalidate|native_commit,COMMIT,op3|p_landing,+1|role/ready/dirty,tag_live|
|rollback|abort_fire,!IDLE/RESPONSE,non-read|U reserved landing OR static staging,+1|release role; WAD rollback; victim unchanged|
|lower acceptance|W_SEND && wb_ready|active WAD payload,+1|free physical role/ready/dirty; FIFO head and sent|
|fill|identity + physical grant|none|ready OR sectors,pending AND~sectors,SRAM bytes|
|external pin|identity+pin_ready|none|one resident pin count,global refs|
|read accept / response consume|req_fire op1 / rsp_fire op1|none|snapshot pin +/-1; mutually exclusive external pin|
|set_done|live/ticket GEN/sent qualified|none|WAD only; never free/revisit possibly reused payload|

The three frontend GEN event classes reservation / native commit / abort are
mutually exclusive by their actual state predicates. They can EACH coincide
with lower_accept, on different slots and even the same physical bank: P1
limits DATA grants, not metadata updates. Therefore two independently computed
GEN results and two decoded write intents are required. In the same-slot
miter, lower_release has the R2 final procedural priority (+1 from OLD GEN),
not cumulative +2. No single 1RW memory or single serialized GEN writer is
assumed. Reset has priority over both; admission saturation remains unchanged.

Other R2 word precedence is retained literally: pin_update then read_add then
read_release; fill then install then hit_write then invalidate then lower;
reserve_resident then reserve_WB then become_WB then install then invalidate
then rollback then lower. All next-state expressions consume old state.
Concurrent different slots, fill+pin and same-slot priority require explicit
miter coverage. WAD GEN is a separate real128x32 table/adder, not payload GEN.

## Candidate A (P0 + real P2 sharing)

Move payload GEN arithmetic from1168 words to two actual shared prefix engines:
frontend + lower. Keep all actual GEN FF and two decoded data/write paths.
The frontend GEN read at IDLE accesses free_landing/free_staging; otherwise
p_landing, except static abort reads p_staging. The same read serves captured
read return (p_old==p_landing for op1), install/native_gen and rollback. This
replaces separate p_landing/p_old/free_staging reads. Independent admission,
fill,pin,WB/lower reads stay independent. The lower read, previously assertion-
only in R2, becomes actual hardware and is fully charged. GEN32 distribution,
write muxes and repeaters are real standard cells, not assumed free buses.

Observational equivalence is cycle-by-cycle on ALL valid/ready/control signals
and every valid-qualified data/identity output. native_gen when !native_commit
is an unconsumed combinational value and may differ because the transactional
read port is shared; no stage, II, acceptance, valid payload, bank choice or
completion order changes. The existing interface commits Tag only on
native_commit. Unqualified data is not compared as an architectural result.

## Candidate B (P1 owner redundancy, isolated after A)

Invariant to prove before implementing: for every live Tag t, mapped PID is a
RESIDENT owned by t; every RESIDENT PID has exactly one live mapped Tag. Reserve
roles/FREE/WB are not residents. Install/rebind changes mapping/role together;
abort preserves old resident; invalidate removes live+resident together;
fill/pin cannot change mapping; lower frees only WB. Generation remains an
independent qualifier. Thus fill owner equality can be replaced by tag_live[t]
&& map[t]==pid ONLY under these inductive reachability invariants. Reserved,
stale generation, reused payload/Tag, held snapshot pins and same-edge admission
must be tested. The new Tag-map read port and comparison must be charged.
Do not move pins/readiness/masks outside the cost cut. Full Tag-index resident
restructuring is separate: requires multiple field write ports and payload to
Tag resolution for external pin; ordinary 1RW SRAM cannot be assumed sufficient.
If its equivalence/ports cannot be established within the bound, STOP that
candidate and retain the qualified A/B source, not a fictitious macro saving.

## State and cost ledger

Keep GEN32 per used payload, WAD128x32 tickets, role,6-bit pins,three4-bit sector
vectors, all ownership until candidate B proof,1024x11 U map,1024 tag_live,
addresses/FIFO/WAD masks and1024-bit data holding registers. B/S fixed resident
map/owner/role proofs remain. Static bypass pruning unchanged. No narrowing,
external/free metadata, timing exceptions or SRAM area substitution. Actual
SRAM146KiB and native Tag/LRU/MSHR/NoC costs UNKNOWN. Four data banks stay P1.
R2's readII4/writeII3/copy/return/arbiter/native-approval gaps remain. No SIM
patch, new official application, or H0/Lane5 performance pairing is authorized.
