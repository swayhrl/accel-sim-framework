# C incremental full-combination cost contract (unmeasured source)

The combined public adapter preserves A's paid frontend CAM1/slice/cycle, separate
WB-completion CAM1, three indexed control views/update lanes, row/incarnation
and original WB UID check before mutation. RO preview consumes the existing
frontend ticket; no second TVD/WAD address CAM is introduced. On a native Tag
miss the paid TVD lookup precedes the one-cycle RO query. The combined path can
therefore add a serial metadata cycle versus isolated RO. A TVD-served read has
no RO query, descriptor or landing; its requester remains in the existing frontend
and ICNT queue. It is not a free extra request record.

RO query still compares existing sharedD512 fields and attached Tag/native-line
index, with one frontend ticket; parallel comparison/control implementation and
physical timing/PPA are unknown. M bypass provides no new line-address map.
Response-ready priority selection over finite1168 entries/shared chains is
explicit control cost. Neither software scans nor debug ownership checks prove
single-port SRAM timing or free hardware lookup.

Data budget1168x128B, Tags1024, shared descriptors512/address32, native line-MSHR128,
WAD/TVD rows128, four P1 banks are unchanged. Role labels now distinguish TVD4 and
RO5 (at least3 bits); their separate states require4 bits. No extra payload RAM,
response buffer, descriptor pool, directory row or unbounded service head. Existing
A fixed-victim quotas, optional-reclaim restrictions and mandatory WB pins persist.

C adds one response_chosen control bit per completion entry (at most one entry
per existing landing) to retain the selected D512 waiter index before bank denial.
The requester pointer/mask live only in the canonical descriptor. Native RO
returns/responses reuse existing FILL/RESPONSE client, original UID32 and
payloadGEN32; the bank scoreboard already has these fields. A per-port current
return UID32 is borrowed from the actual held packet during the callback, not
per-packet new NoC bits or a data buffer. RO Tag generation remains64 bits. The
new boolean selecting native request ids is static adapter configuration; module
reference-port fixtures retain their explicitly separate fake-pointer scope.

Actual native operations, duplicate lower sectors/bytes, independently outstanding
lines, completed requester rate/physical boundaries and bank retries remain source
counters, NOT measured results in this pack. A's common lower observer counts each
RO packet once; TVD accepted-read coverage does not inflate RO descriptor admits.
Per-slice maxima need not coincide; waits overlap; neither sum is a GPU stall.
Exact ABI sizeof, area, frequency and PPA are UNKNOWN. Old WB R3 PPA does not apply.
