# R2 responsibility and equivalence argument

R1 is frozen at09de19579. Contract f2a2fec3; finite SIM9bd30ed9. No formal
simulator or application source is modified. Full1024/1168/128/GEN32 capacities.

R1 responsibility (same Nangate typical, SDC0.883392226ns):

|Cut|B16|S64|Unified|
|---|---:|---:|---:|
|resident metadata own area|1136113.664|1136113.664|1298675.840|
|static WB-only metadata|5673.248|22692.992|included above|
|top logic/selection/decode|843230.906|877285.822|1141716.688|
|Tag-map words|84439.040|84439.040|84439.040|
|arbiter|514.178|514.178|514.178|

B16/S64 worst path p_old register -> selected generation/increment -> native_gen;
B16 launch fanout1027, cap1715.14fF, delay4.1965ns; selected increment output
fanout1025/cap1705.76fF/delay8.6714ns. Unified launch word0 generation[2] ->
full-pool first-free priority chain -> install_ok/req_ready/fire -> p_tag[8].
WAD CAM also feeds req_ready and is charged:128 full64-bit address comparators,
OR hazard reduction, generation-qualified first-free. No claim that its cost
or delay is zero. R1 WNS=-13.614565/-13.612103/-36.605915ns respectively.

Changes, identical algorithm where applicable:

1. Four292-leaf balanced first-one trees replace the1168-slot serial landing
loop. req_tag[1:0] chooses a bank; increasing row order is increasing physical
ID within that bank. This returns exactly the R1 lowest eligible PID, including
empty/exhausted generation cases. Staging16/64 and WAD128 use the same tree.
No free-list state, allocation-order change, extra cycle, retry or rollback.
free_bank_exists intentionally ignores generation, preserving blocked reporting.
2. Explicit16-word local muxes followed by group OR selection retain every
runtime metadata read. Per-word install generation now uses its own unchanged
generation and the same old_live step1/2. It no longer receives the shared
selected/incremented32-bit generation bus. Reservation, invalidate, rollback
and lower_accept increments remain; no width/saturation/priority change.
3. Static mapping proof below removes only redundant state. Unified retains
all dynamic Tag-map and owner state. No metadata is excluded from mapping.

Static invariants by induction, separately B16 and S64:
- Reset has no live Tag. The sole resident install target is p_landing=old_pid.
- For MODE!=1, allocation never changes p_landing to free_landing. Initially
old_pid=req_tag for a nonlive Tag. Each successful native install maps that
Tag back to exactly the same slot. Inductively any live Tag t maps to PID t.
- Dirty static eviction copies bytes to staging [1152,1168) for B16 or
[1104,1168) for S64; it does not relocate the resident landing. WAD records the
staging PID/address/generation. Abort preserves the old resident mapping.
Invalidate removes only live validity. No other writer mutates Tag mapping.
- Only resident installation/reservation can write owner. Static resident
slot m<N_TAG can only be installed by Tag m. Runtime fill owner comparison is
qualified by role==RESIDENT and generation match. At reset/FREE the old owner
is unobservable; hardwired m differs from R1's reset0 only under that guard.
WB-only staging never serves as resident; its owner fields remain pruned by
SUPPORT_RES=0. Unified lacks these invariants and keeps dynamic owner FFs.

Still stateful and costed: live/role, generation32, pins6, ready/pending/dirty4,
WAD address/identity/generation/byte masks/FIFO, transaction/control registers,
real1024-bit access/copy/response/WB holding data and all variable handles.

No frontend/bank/SRAM/approval phase is added in R2. Existing R1 SIM/RTL gaps
remain; no timing closure is implied by this source-level equivalence argument.
Dynamic late rollback after destructive native commit and whole-app numeric
correctness remain unqualified. No new SIM-performance pairing is authorized.
